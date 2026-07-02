from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Satisfiable
from flamapy.metamodels.dnnf_metamodel.models import DDNNFModel
from flamapy.metamodels.dnnf_metamodel.operations.d4_runner import d4_model_count


class DDNNFSatisfiable(Satisfiable):
    """Whether the feature model is satisfiable (non-void): its exact model count is non-zero."""

    def __init__(self) -> None:
        self._result = False

    def is_satisfiable(self) -> bool:
        return self._result

    def get_result(self) -> bool:
        return self._result

    def execute(self, model: VariabilityModel) -> 'DDNNFSatisfiable':
        dnnf_model = cast(DDNNFModel, model)
        self._result = d4_model_count(dnnf_model.dimacs_path) > 0
        return self
