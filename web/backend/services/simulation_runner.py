"""Runs simulations off the request thread and reports progress.

The predecessor spelled the whole chart list out here a second time, duplicating
`run_strategy_comparison.generate_plots`. It now calls the one declared suite in
`envistra.utilities.PlotSuite`, so the CLI and the UI cannot drift apart.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from envistra.bootstrap import initialize_model
from envistra.config import Loader
from envistra.config.GlobalConfig import GlobalConfig
from envistra.utilities.PlotBuilder import PlotBuilder
from envistra.utilities.PlotSuite import TOTAL_PLOTS, run_plot_suite

from ..config import RESULTS_FOLDER
from .results_manager import IN_PROGRESS_MARKER


class SimulationRunner:
    """One simulation at a time per worker, off the event loop."""

    def __init__(self, max_workers: int = 2):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def _run_sync(self, steps: int, seed=None, progress=None):
        def report(payload):
            if progress is not None:
                progress(payload)

        report({"type": "started", "message": "Loading configuration",
                "step": 0, "total_steps": steps})

        # Configuration is read fresh for every run, so edits made through the
        # API since the last run take effect.
        model, _, companies, _ = initialize_model(seed=seed)
        drawn = Loader.plotted(companies)

        report({"type": "initialized",
                "message": f"{len(model.agents)} agents, {len(drawn)} plotted",
                "step": 0, "total_steps": steps})

        start_year = GlobalConfig.Startup.Year
        for step in range(1, steps + 1):
            model.step()
            report({"type": "step", "step": step, "total_steps": steps,
                    "year": start_year + step - 1,
                    "message": f"Step {step} of {steps}",
                    "progress": round(step / steps * 50, 1)})

        history = model.datacollector.get_agent_vars_dataframe()

        plotter = PlotBuilder(
            model_history=history,
            companies=drawn,
            plots=model.simulationConfig["plots"],
            result_folder=str(RESULTS_FOLDER),
            base_name="StrategyComparison",
        )

        def on_plot(done, total, title):
            report({
                "type": "plot", "plot_name": title,
                "plot_path": f"/api/simulations/{_folder_name(plotter)}/images/{title}."
                             f"{plotter.format}",
                "message": f"Generated {title}",
                "step": done, "total_steps": total,
                # Stepping is the first half of the work, plotting the second.
                "progress": round(50 + done / total * 50, 1),
            })

        # The folder exists from here on; mark it so it cannot be renamed or
        # deleted while charts are still being written into it.
        marker = Path(plotter.output_folder) / IN_PROGRESS_MARKER
        marker.touch()
        try:
            run_plot_suite(plotter, steps=steps, on_plot=on_plot, seed=seed)
        finally:
            marker.unlink(missing_ok=True)
        return _folder_name(plotter)

    async def run_strategy_comparison(self, steps: int, seed=None, progress_callback=None):
        """Await a run without blocking the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor, self._run_sync, steps, seed, progress_callback)


def _folder_name(plotter) -> str:
    return Path(plotter.output_folder).name


#: How many plot events a client should expect, so a progress bar can size
#: itself. The predecessor advertised 21 while emitting 25.
EXPECTED_PLOTS = TOTAL_PLOTS

runner = SimulationRunner()
