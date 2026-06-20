from dataclasses import dataclass

from matmat.workflows.engines.identity import AbstractEngineIdentity


@dataclass(kw_only=True)
class EngineEEIOIdentity(AbstractEngineIdentity):
    """
    Attributes
    ----------
        path_in:
            accounts: str
                Path to the accounts directory
            shock: str
                Path to the shock directory (optional)
            bridges: str
                Path to the bridges file (optional)
        path_out: str
            The path to the directory to save the output accounts
        system_calcul_strategy: str
            The system calculation strategy
        shall_calculate_mapping: bool
            True if mapping data shall be calculated. Default to False.
        extension_names: list[str]
            The names of the extensions to process
    """

    system_calcul_strategy: str
    shall_calculate_mapping: bool = False
    extension_names: list[str]
