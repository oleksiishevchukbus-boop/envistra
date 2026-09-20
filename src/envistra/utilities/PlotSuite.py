"""The standard chart set for a simulation run.

Declared once, in one place. The predecessor spelled this list out twice — in
`run_strategy_comparison.generate_plots` and again in the web backend's
`SimulationRunner`, 29 versus 28 plot calls with 19 shared titles — so a chart
changed in one and not the other silently diverged between the CLI and the UI.

The titles matter beyond the chart: each becomes the image filename, and the
backend groups images for the UI by matching on them. Declaring them here makes
them single-sourced.

`on_plot(done, total, title)` is called after each chart, which is how the
backend drives its progress bar. The CLI passes nothing.
"""
from envistra.config.Enums import CompanyAgentFields as F
from envistra.utilities.ConfigSerializer import build_run_metadata

MONEY = "$\\cdot 10^9$"


class Chart:
    """One chart: either a raw field, or a series computed from the frame."""

    def __init__(self, title, ylabel, field=None, compute=None,
                 skip_first=False, show_zero_line=False):
        self.title = title
        self.ylabel = ylabel
        self.field = field
        self.compute = compute
        self.skip_first = skip_first
        self.show_zero_line = show_zero_line

    def draw(self, plotter):
        if self.compute is not None:
            return plotter.plot_computed(
                self.compute, title=self.title, ylabel=self.ylabel,
                skip_first=self.skip_first, show_zero_line=self.show_zero_line)
        return plotter.plot_field(
            self.field, title=self.title, ylabel=self.ylabel,
            skip_first=self.skip_first, show_zero_line=self.show_zero_line)


#: Order is the order the UI reports progress in.
CHARTS = [
    # Basics
    Chart("Assets", f"Assets ({MONEY})", field=F.ASSETS),
    Chart("Expenses", f"Expenses ({MONEY})", field=F.EXPENSES),
    Chart("Expenses Reduction", f"Expenses ({MONEY})", field=F.EXPENSES_REDUCTION),
    Chart("Revenue", f"Revenue ({MONEY})", field=F.REVENUE),
    Chart("Operational Net Revenue", f"Operational Net Revenue ({MONEY})",
          field=F.OPERATIONAL_NET_REVENUE, show_zero_line=True),
    Chart("Net Revenue", f"Net Revenue ({MONEY})", field=F.NET_REVENUE, show_zero_line=True),

    # Pollution
    Chart("Pollution", f"Pollution ({MONEY})", field=F.POLLUTION),
    Chart("Expected Pollution", f"Expected Pollution ({MONEY})",
          field=F.EXPECTED_POLLUTION, skip_first=True),
    Chart("Pollution Difference", "Pollution Difference",
          compute=lambda df: df[F.POLLUTION] - df[F.EXPECTED_POLLUTION],
          skip_first=True, show_zero_line=True),

    # Quota
    Chart("Quota", f"Quota ({MONEY})", field=F.QUOTA, skip_first=True),
    Chart("Quota Share", "Quota Share", field=F.QUOTA_SHARE, skip_first=True),
    Chart("Base Quota Exceedance", f"Quota Exceedance ({MONEY})",
          compute=lambda df: df[F.POLLUTION] - df[F.QUOTA],
          skip_first=True, show_zero_line=True),
    Chart("Quota Exceedance", f"Quota Exceedance ({MONEY})",
          compute=lambda df: (df[F.POLLUTION] - df[F.QUOTA]
                              - df[F.BOUGHT_QUOTA_AMOUNT] + df[F.SOLD_QUOTA_AMOUNT]),
          skip_first=True, show_zero_line=True),
    Chart("Quota Exceedance Penalty", f"Quota Exceedance Penalty ({MONEY})",
          field=F.QUOTA_EXCEEDANCE_PENALTY, show_zero_line=True),

    # Quota trade
    Chart("Quota to Trade Amount", f"Quota to Trade Amount ({MONEY})",
          compute=lambda df: df[F.QUOTA_TO_BUY_AMOUNT] - df[F.QUOTA_TO_SELL_AMOUNT],
          show_zero_line=True),
    Chart("Quota Traded Amount", f"Quota Traded Amount ({MONEY})",
          compute=lambda df: df[F.BOUGHT_QUOTA_AMOUNT] - df[F.SOLD_QUOTA_AMOUNT],
          show_zero_line=True),
    Chart("Quota Trade Revenue", f"Quota Trade Revenue ({MONEY})",
          compute=lambda df: df[F.SOLD_QUOTA_REVENUE] - df[F.BOUGHT_QUOTA_EXPENSES],
          show_zero_line=True),
    Chart("Quota Unit Price", "Quota Unit Price", field=F.QUOTA_UNIT_PRICE),

    # Ratios
    Chart("Revenue To Expenses Ratio", "Revenue To Expenses Ratio",
          field=F.REVENUE_TO_EXPENSES_RATIO),
    Chart("Pollution To Expenses Ratio", "Pollution To Expenses Ratio",
          field=F.POLLUTION_TO_EXPENSES_RATIO),

    # Efficiency
    Chart("Financial Efficiency", "Financial Efficiency", field=F.FIN_EFF),
    Chart("Ecological Efficiency", "Ecological Efficiency", field=F.ECO_EFF),
    Chart("Financial Efficiency Investments", f"Financial Efficiency Investments ({MONEY})",
          field=F.FIN_EFF_INVEST),
    Chart("Ecological Efficiency Investments", f"Ecological Efficiency Investments ({MONEY})",
          field=F.ECO_EFF_INVEST),
]

#: What a caller should expect to report. Derived, not a hand-kept number — the
#: predecessor's backend advertised 21 while emitting 25 progress events.
TOTAL_PLOTS = len(CHARTS)


def run_plot_suite(plotter, steps, on_plot=None, seed=None):
    """Draw every chart, compute the metrics, and write the run record.

    Returns the run metadata, which is also saved as `run_config.json` beside
    the charts along with `model_history.csv`.
    """
    for index, chart in enumerate(CHARTS, start=1):
        chart.draw(plotter)
        if on_plot is not None:
            on_plot(index, TOTAL_PLOTS, chart.title)

    mlp_metrics = plotter.compute_all_mlp_metrics(
        F.POLLUTION, F.EXPECTED_POLLUTION, print_results=False)

    metadata = build_run_metadata(plotter.companies, simulation_steps=steps,
                                  mlp_metrics=mlp_metrics, seed=seed)
    plotter.save_run_config(metadata)
    plotter.save_model_history()
    return metadata
