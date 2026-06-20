from dataclasses import dataclass

from matmat.workflows.adapters.identity import AbstractAdapterIdentity


@dataclass(kw_only=True)
class Exiobase3EEIOIdentity(AbstractAdapterIdentity):
    """
    Attributes
    ----------
        version : str
            Version identifier of the Exiobase database.
            (e.g., '3.8.2' or '3.9.4').
        system : str
            Symmetrization assumption used to transform supply-use tables.
            (e.g., 'pxp' or 'ixi').
        base_year : int
            Target year for which the MRIO data should be loaded.
            (e.g., 2015 or 2019).
        extension_names : list of str
            List of environmental and socioeconomic extension names to extract
            from the database.
    """

    version: str
    system: str
    base_year: int
    extension_names: list[str]
