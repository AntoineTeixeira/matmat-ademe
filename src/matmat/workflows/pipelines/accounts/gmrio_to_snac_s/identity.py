from dataclasses import dataclass

from matmat.workflows.pipelines.identity import AbstractPipelineIdentity


@dataclass(kw_only=True)
class GmrioToSnacSIdentity(AbstractPipelineIdentity):
    """
    Attributes
    ----------
        extension_names : list of str
            List of environmental and socioeconomic extension names to extract
            from the database.
    """

    extension_names: list[str]
    m_row_mode: str = None
    calculate_accounts: bool = False
