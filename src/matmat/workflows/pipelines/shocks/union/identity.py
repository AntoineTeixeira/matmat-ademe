from dataclasses import dataclass

from matmat.workflows.pipelines.identity import AbstractPipelineIdentity


@dataclass(kw_only=True)
class PipelineUnionIdentity(AbstractPipelineIdentity):
    """
    Attributes
    ----------
        path_in:
            shocks: dict[str, list[str]]
                For each aggregation level, the list of shocks associated
            multi_bridge: str
                The path to the multi bridge file or to the directory containing
                the detail levels file "bridge_matrices.xlsx"
        path_out: str
            The path to the directory to save the output shock
        multi_bridge_filter_level : str
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges)
    """

    multi_bridge_filter_level: str
