"""Writes configuration back to disk, validated and atomically.

The loader refuses invalid configuration rather than falling back to defaults,
which is deliberate — but it means a bad write leaves the whole application
unable to start. So every function here **validates by building the object
through the loader's own parser first**, and only then replaces the file, using
a temporary file and `os.replace` so a failure leaves the previous content
intact.

It also enforces referential integrity, which the predecessor's API never did: a
strategy cannot be deleted while a company references it.
"""
import json
import os
import re
import tempfile
from pathlib import Path

from envistra.config import Loader
from envistra.config.Errors import ConfigError

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(name):
    """Derive a filename stem from a display name."""
    stem = _SLUG_STRIP.sub("-", str(name).lower()).strip("-")
    if not stem:
        raise ConfigError(message=f"{name!r} does not yield a usable filename")
    return stem


def _write_atomic(path, data):
    """Replace `path` with `data` as JSON, or leave it untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return path


# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #

def strategy_path(strategy_id, directory=None):
    directory = Path(directory) if directory else Loader.config_dir() / "strategies"
    return directory / f"{strategy_id}.json"


def save_strategy(strategy_id, data, directory=None):
    """Validate and write one strategy file.

    Names must stay unique across files, because the API addresses a strategy by
    its display name.
    """
    path = strategy_path(strategy_id, directory)
    Loader._build_strategy(path, data)  # raises ConfigError on anything invalid

    for other_id, other in Loader.load_strategies(path.parent).items():
        if other_id != strategy_id and other.name == data.get("name"):
            raise ConfigError(path, f"strategy name {data['name']!r} is already used by "
                                    f"{other_id}.json", field="name")
    return _write_atomic(path, data)


def delete_strategy(strategy_id, directory=None):
    """Remove a strategy, unless a company still references it."""
    path = strategy_path(strategy_id, directory)
    if not path.is_file():
        raise ConfigError(path, "strategy not found")

    companies_dir = path.parent.parent / "companies"
    users = [c.name for c in Loader.load_companies(
        Loader.load_strategies(path.parent), companies_dir) if c.strategyId == strategy_id]
    if users:
        raise ConfigError(
            path,
            f"{len(users)} compan{'y' if len(users) == 1 else 'ies'} still use this strategy: "
            + ", ".join(repr(u) for u in users)
            + "\n  point them at another strategy first",
            field="strategy")

    if len(list(path.parent.glob("*.json"))) <= 1:
        raise ConfigError(path, "this is the last strategy; at least one must remain")

    path.unlink()
    return path


# --------------------------------------------------------------------------- #
# Companies
# --------------------------------------------------------------------------- #

def company_path(company_id, directory=None):
    directory = Path(directory) if directory else Loader.config_dir() / "companies"
    return directory / f"{company_id}.json"


def save_company(company_id, data, directory=None, strategies=None):
    """Validate and write one company file.

    Enforces exactly what the loader enforces, so a write cannot produce a
    configuration that then fails to load: the strategy must resolve, names must
    be unique, and `plot` cannot be true while `enabled` is false.
    """
    path = company_path(company_id, directory)
    if strategies is None:
        strategies = Loader.load_strategies(path.parent.parent / "strategies")

    Loader._build_company(path, data, strategies)  # raises ConfigError

    others = [c for c in Loader.load_companies(strategies, path.parent)
              if c.configId != company_id]

    if any(c.name == data.get("name") for c in others):
        raise ConfigError(path, f"company name {data['name']!r} is already used", field="name")

    if not data.get("enabled", True) and not any(c.enabled for c in others):
        raise ConfigError(path, "this is the last enabled company; "
                                "there would be no agents to simulate", field="enabled")
    return _write_atomic(path, data)


def delete_company(company_id, directory=None):
    """Remove a company, unless it is the last enabled one."""
    path = company_path(company_id, directory)
    if not path.is_file():
        raise ConfigError(path, "company not found")

    strategies = Loader.load_strategies(path.parent.parent / "strategies")
    remaining = [c for c in Loader.load_companies(strategies, path.parent)
                 if c.configId != company_id]
    if not any(c.enabled for c in remaining):
        raise ConfigError(path, "this is the last enabled company; "
                                "there would be no agents to simulate")

    path.unlink()
    return path


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #

def save_environment(data, path=None):
    """Validate and write the environment regime.

    Validation runs before anything is applied or written, so a rejected
    document leaves both the file and the live config classes untouched.
    """
    path = Path(path) if path else Loader.config_dir() / "environment.json"
    Loader.parse_environment(path, data)  # raises ConfigError
    return _write_atomic(path, data)


def save_simulation(data, path=None):
    """Validate and write run-wide settings (`config/simulation.json`).

    Read afresh by every run, so nothing needs applying after the write.
    """
    path = Path(path) if path else Loader.config_dir() / "simulation.json"
    Loader.parse_simulation(path, data)  # raises ConfigError
    return _write_atomic(path, data)
