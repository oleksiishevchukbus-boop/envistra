"""Plot suite for simulation results.

Each run writes into its own timestamped folder under the results directory.
Output settings — dpi, figure size, format — come from `config/simulation.json`.

Line colour comes from the company's `color` in `config/companies/*.json`; the
loader assigns a distinct one to any company that does not declare it. The
predecessor cycled a four-entry palette, which silently repeated colours once a
chart held more than four agents.
"""
import json
import os
import re
from datetime import datetime
from typing import Callable, Optional

import matplotlib

# Headless: the web backend plots inside a worker thread, and no caller displays.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn import metrics  # noqa: E402

from envistra.config.Enums import CompanyAgentFields  # noqa: E402

#: Used for the "real data" series in model-vs-source charts.
SOURCE_COLOR = "#DF4E4E"
MODEL_COLOR = "#4E6EDF"

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def slugify(text):
    """Make a string safe to use as a filename.

    Plot titles become filenames, and company names now come from user-authored
    JSON, so a name containing `/` or `:` would otherwise produce an unwritable
    path on Windows.
    """
    cleaned = _UNSAFE.sub("-", str(text)).strip(" .")
    return cleaned or "plot"


class PlotBuilder:
    """Builds the chart suite for one simulation run."""

    def __init__(
        self,
        model_history: pd.DataFrame,
        companies: list,
        start_year: int = 2010,
        plots: Optional[dict] = None,
        base_name: str = "Plot",
        figsize: Optional[tuple] = None,
        dpi: Optional[int] = None,
        result_folder: Optional[str] = None,
        image_format: Optional[str] = None,
    ):
        plots = plots or {}
        self.model_history = model_history
        self.companies = companies
        self.start_year = start_year
        self.figsize = tuple(figsize or plots.get("figsize", (12, 5)))
        self.dpi = dpi or plots.get("dpi", 600)
        self.format = image_format or plots.get("format", "jpg")
        self.result_folder = result_folder or plots.get("resultsFolder", "results")
        self.base_name = base_name

        self._company_dataframes: Optional[dict] = None
        self.output_folder = self._create_output_folder()

    def _create_output_folder(self) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = os.path.join(self.result_folder, f"{slugify(self.base_name)}_{timestamp}")
        os.makedirs(output_path, exist_ok=True)
        return output_path

    def prepare_company_dataframes(self) -> dict:
        """One DataFrame per company, indexed by year.

        Cached: mutating `model_history` or `companies` afterwards has no effect.
        """
        if self._company_dataframes is not None:
            return self._company_dataframes

        self._company_dataframes = {}
        missing = []
        for company in self.companies:
            df = self.model_history[
                self.model_history[CompanyAgentFields.NAME] == company.name].copy()
            if df.empty:
                missing.append(company.name)
            df.index = [self.start_year + int(step) - 1 for step, _ in df.index]
            self._company_dataframes[company.name] = df

        if missing:
            # The predecessor plotted an empty frame and a legend entry with no line.
            raise ValueError(
                "no rows in the model history for: " + ", ".join(repr(n) for n in missing)
                + "\n  the company set does not match the run that produced this history")
        return self._company_dataframes

    # ----------------------------------------------------------------- output

    def _finish(self, fig, ax, title, ylabel, filename, show_zero_line=False):
        """Label, save and close. Held per-figure, not via the pyplot globals.

        The predecessor called the module-level `plt.savefig`/`plt.close`, so two
        simulations plotting concurrently — which the web backend does, on a
        two-worker pool — could write one run's chart into the other's folder.
        """
        if show_zero_line:
            ax.axhline(0, color="black", linewidth=0.25, linestyle="--")
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig.tight_layout()

        name = slugify(filename if filename else title)
        path = os.path.join(self.output_folder, f"{name}.{self.format}")
        fig.savefig(path, dpi=self.dpi)
        plt.close(fig)
        return path

    # ------------------------------------------------------------ multi-agent

    def plot_field(self, field, title=None, ylabel=None, skip_first=False,
                   show_zero_line=False, filename=None):
        """One field, one line per company."""
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)
        field_str = str(field)

        for company in self.companies:
            df = dfs[company.name]
            index, values = (df.index[1:], df[field].iloc[1:]) if skip_first else (df.index, df[field])
            ax.plot(index, values, label=company.name, color=company.color)

        return self._finish(fig, ax, title or field_str, ylabel or field_str,
                            filename, show_zero_line)

    def plot_computed(self, compute_func: Callable[[pd.DataFrame], pd.Series], title, ylabel,
                      skip_first=False, show_zero_line=False, filename=None):
        """One derived series, one line per company."""
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)

        for company in self.companies:
            df = dfs[company.name]
            computed = compute_func(df)
            index, values = (df.index[1:], computed.iloc[1:]) if skip_first else (df.index, computed)
            ax.plot(index, values, label=company.name, color=company.color)

        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    # ----------------------------------------------------------- single agent

    def _first(self, dfs):
        """The company these single-agent charts describe."""
        company = self.companies[0]
        return company, dfs[company.name]

    def plot_model_vs_source(self, model_field, source_df, source_field, title, ylabel,
                             model_label="Modelled", source_label="Real",
                             show_zero_line=False, filename=None):
        """Modelled series against the historical series it is calibrated to."""
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(source_df.index, source_df[source_field], label=source_label, color=SOURCE_COLOR)
        _, df = self._first(dfs)
        ax.plot(df.index, df[model_field], label=model_label, color=MODEL_COLOR)

        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    def plot_model_vs_source_computed(self, model_field, source_df, source_compute_func,
                                      title, ylabel, model_label="Modelled",
                                      source_label="Real", show_zero_line=False, filename=None):
        """As above, where the historical series has to be derived first."""
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(source_df.index, source_compute_func(source_df), label=source_label,
                color=SOURCE_COLOR)
        _, df = self._first(dfs)
        ax.plot(df.index, df[model_field], label=model_label, color=MODEL_COLOR)

        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    def plot_multi_field(self, fields, title, ylabel, show_zero_line=False, filename=None):
        """Several fields of one company on shared axes.

        Colour varies by field here, not by company, so it uses a fixed cycle
        rather than the company palette.
        """
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)
        _, df = self._first(dfs)

        cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        for i, (field, label) in enumerate(fields):
            ax.plot(df.index, df[field], label=label, color=cycle[i % len(cycle)])

        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    def plot_single_field(self, field, title, ylabel, label,
                          show_zero_line=False, filename=None):
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)
        company, df = self._first(dfs)
        ax.plot(df.index, df[field], label=label, color=company.color)
        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    def plot_single_computed(self, compute_func, title, ylabel, label,
                             show_zero_line=False, filename=None, skip_first=False):
        dfs = self.prepare_company_dataframes()
        fig, ax = plt.subplots(figsize=self.figsize)
        company, df = self._first(dfs)
        computed = compute_func(df)
        index, values = (df.index[1:], computed.iloc[1:]) if skip_first else (df.index, computed)
        ax.plot(index, values, label=label, color=company.color)
        return self._finish(fig, ax, title, ylabel, filename, show_zero_line)

    # --------------------------------------------------------------- metrics

    def compute_mlp_metrics(self, actual_field, predicted_field, company_name,
                            skip_first=True, save_to_file=True, print_results=True) -> dict:
        """Regression metrics for one company's pollution forecast.

        `skip_first` drops step one, where the predicted value has no history to
        work from and is still at its initial value.
        """
        df = self.prepare_company_dataframes()[company_name]
        actual = df[actual_field].iloc[1:] if skip_first else df[actual_field]
        predicted = df[predicted_field].iloc[1:] if skip_first else df[predicted_field]

        mse = metrics.mean_squared_error(actual, predicted)
        results = {
            "r2": metrics.r2_score(actual, predicted),
            "mae": metrics.mean_absolute_error(actual, predicted),
            "mse": mse,
            "rmse": float(np.sqrt(mse)),
        }

        lines = [
            f"--- Model Validation Metrics {company_name} ---",
            f"R-squared (R2 Score): {results['r2']:.4f}",
            f"Mean Absolute Error (MAE): {results['mae']:.4f}",
            f"Mean Squared Error (MSE): {results['mse']:.4f}",
            f"Root Mean Squared Error (RMSE): {results['rmse']:.4f} \n",
        ]
        if print_results:
            print("\n".join(lines))
        if save_to_file:
            path = os.path.join(self.output_folder,
                                f"{slugify(f'Pollution Prediction Metrics - {company_name}')}.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
        return results

    def compute_all_mlp_metrics(self, actual_field, predicted_field, skip_first=True,
                                save_to_file=True, print_results=True) -> dict:
        return {
            company.name: self.compute_mlp_metrics(
                actual_field, predicted_field, company.name,
                skip_first=skip_first, save_to_file=save_to_file, print_results=print_results)
            for company in self.companies
        }

    # ----------------------------------------------------------------- saving

    def save_run_config(self, metadata: dict, filename: str = "run_config.json") -> str:
        path = os.path.join(self.output_folder, filename)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(metadata, fh, indent=2, ensure_ascii=False)
        return path

    def save_model_history(self, filename: str = "model_history.csv") -> str:
        """The full history for every agent, not only the plotted subset."""
        path = os.path.join(self.output_folder, filename)
        self.model_history.to_csv(path)
        return path
