from dataclasses import dataclass

from matmat.workflows.pipelines.identity import AbstractPipelineIdentity


@dataclass(kw_only=True)
class PipelineAggregationIdentity(AbstractPipelineIdentity):
    """
    path_in:
        accounts: str
            Path to the accounts to aggregate
        bridges: str
            Path to the bridges file
    path_out: str
        The path to the directory to save the aggregated accounts
    extension_names: list[str]
        List of names of the extensions to include in the aggregated accounts
    calculate_accounts: bool
        True if the accounts shall be calculated after aggregation,
        False otherwise. Default to False.
    """

    extension_names: list[str]
    calculate_accounts: bool = False
