#!/usr/bin/env python
"""Start the ENVISTRA web stack — API and interface — with one command.

    python run_web.py

Runs uvicorn and the Vite dev server together, interleaves their output, and
stops both on Ctrl+C. Checks the things that otherwise fail confusingly: a
missing package, missing node modules, missing workbooks, or a port already in
use.
"""
import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "web" / "frontend"

# Colour only when writing to a terminal, and avoid characters a legacy Windows
# console code page cannot encode.
_TTY = sys.stdout.isatty()
RESET = "\033[0m" if _TTY else ""
DIM = "\033[2m" if _TTY else ""
COLORS = {"api": "\033[36m", "ui": "\033[35m", "!": "\033[31m"} if _TTY else {}


def say(tag, message):
    color = COLORS.get(tag, "")
    line = f"{color}{tag:>3}{RESET} | {message}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"), flush=True)


def port_is_free(port):
    """True only if nothing answers on the port, over either IP family.

    A dev server left running on IPv6 is invisible to a v4-only probe, and the
    failure then surfaces as an unhelpful "address in use" from the child.
    """
    for family, address in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as probe:
                probe.settimeout(0.4)
                if probe.connect_ex((address, port)) == 0:
                    return False
        except OSError:
            continue  # family unavailable
    return True


def preflight(args):
    """Fail early, with the fix, rather than mid-run."""
    problems = []

    try:
        import envistra  # noqa: F401
    except ImportError:
        problems.append("The envistra package is not installed.\n"
                        '      Fix:  pip install -e ".[web]"')

    missing = [m for m in ("fastapi", "uvicorn") if not _importable(m)]
    if missing:
        problems.append(f"Missing Python packages: {', '.join(missing)}.\n"
                        '      Fix:  pip install -e ".[web]"')

    if not (FRONTEND / "node_modules").is_dir():
        problems.append("The interface has no node_modules.\n"
                        f"      Fix:  cd {FRONTEND.relative_to(ROOT)} && npm install")

    if shutil.which("npm") is None:
        problems.append("npm is not on PATH. Node.js 18+ is required for the interface.")

    # Workbooks are gitignored, so a fresh clone has none. The app starts without
    # them; the failure only appears when a simulation runs.
    workbooks = list((ROOT / "data").glob("**/*.xlsx")) if (ROOT / "data").is_dir() else []
    if not workbooks:
        problems.append("No .xlsx workbooks under data/ - simulations will fail.\n"
                        "      They are not committed on purpose; see data/README.md")

    for port, what in ((args.api_port, "API"), (args.ui_port, "interface")):
        if not port_is_free(port):
            problems.append(f"Port {port} is already in use, needed for the {what}.\n"
                            "      Stop what is using it, or pass a different port.")

    if problems:
        say("!", "Cannot start:")
        for problem in problems:
            print(f"    - {problem}")
        return False

    say("api", f"{len(workbooks)} workbooks, config at {os.environ.get('ENVISTRA_CONFIG_DIR', 'config/')}")
    return True


def _importable(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def pump(stream, tag):
    """Forward a child's output, prefixed so the two are distinguishable."""
    for line in iter(stream.readline, ""):
        line = line.rstrip()
        if line:
            say(tag, line)
    stream.close()


def start(command, tag, cwd, env=None):
    process = subprocess.Popen(
        command, cwd=str(cwd), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
        # Keep Ctrl+C from reaching children directly on Windows; they are shut
        # down deliberately below so neither is left orphaned.
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        # POSIX: own process group, so the whole tree can be signalled at once.
        start_new_session=(os.name != "nt"),
    )
    threading.Thread(target=pump, args=(process.stdout, tag), daemon=True).start()
    return process


def stop(process, tag):
    """Stop a child and everything it spawned.

    Both children spawn their own: uvicorn's reloader runs the server in a
    subprocess, and npm runs vite in one. Terminating only the parent leaves the
    real server holding the port, so the whole tree goes.
    """
    if process.poll() is not None:
        return
    say(tag, "stopping")

    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, check=False)
    else:
        import signal
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            process.terminate()

    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()


def main():
    parser = argparse.ArgumentParser(description="Run the ENVISTRA web stack.")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--ui-port", type=int, default=5173)
    parser.add_argument("--no-reload", action="store_true",
                        help="do not restart the API when Python files change")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not preflight(args):
        return 1

    api_command = [sys.executable, "-m", "uvicorn", "web.backend.main:app",
                   "--port", str(args.api_port)]
    if not args.no_reload:
        api_command.append("--reload")

    # Vite proxies /api and /ws to the API; tell it where the API actually is,
    # so a non-default port still works.
    ui_env = {**os.environ, "ENVISTRA_API_TARGET": f"http://localhost:{args.api_port}"}
    npm = shutil.which("npm")
    ui_command = [npm, "run", "dev", "--", "--port", str(args.ui_port), "--strictPort"]

    say("api", f"starting on http://localhost:{args.api_port}  (docs at /docs)")
    api = start(api_command, "api", ROOT)
    say("ui", f"starting on http://localhost:{args.ui_port}")
    ui = start(ui_command, "ui", FRONTEND, env=ui_env)

    url = f"http://localhost:{args.ui_port}"
    try:
        for _ in range(60):
            time.sleep(0.5)
            if api.poll() is not None or ui.poll() is not None:
                break
            if not port_is_free(args.ui_port) and not port_is_free(args.api_port):
                print()
                say("ui", f"{DIM}ready - open {url}  (Ctrl+C to stop){RESET}")
                if not args.no_browser:
                    webbrowser.open(url)
                break

        while api.poll() is None and ui.poll() is None:
            time.sleep(0.5)

        # One died; the other is useless on its own.
        dead = "api" if api.poll() is not None else "ui"
        say("!", f"the {dead} process exited - shutting the other down")
        return 1
    except KeyboardInterrupt:
        print()
        return 0
    finally:
        stop(ui, "ui")
        stop(api, "api")


if __name__ == "__main__":
    sys.exit(main())
