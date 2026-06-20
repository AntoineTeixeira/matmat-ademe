from dataclasses import dataclass

from matmat.workflows.adapters.identity import AbstractAdapterIdentity


@dataclass(kw_only=True)
class AdapterManualIdentity(AbstractAdapterIdentity):
    """
    Attributes
    ----------
        path_in:
            manual_param_file: str
                The path to the manual param Excel file
            detail_levels_file: str
                The path to the detail levels file or to the directory containing
                the detail levels file "detail_levels.xlsx"
        base_year : int
            The base year of the shock
        scenario_names : list[str]
            The scenario names to process from the input file
        proj_years : list[int]
            The projected years to process from the input file
        extension_names : list[str]
            The extension names to process from the input file
    """

    base_year: int
    scenario_names: list[str]
    proj_years: list[int]
    extension_names: list[str]
