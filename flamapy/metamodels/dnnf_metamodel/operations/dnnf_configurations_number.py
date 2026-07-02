from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import ConfigurationsNumber
from flamapy.metamodels.dnnf_metamodel.models import DDNNFModel
from flamapy.metamodels.dnnf_metamodel.operations.d4_runner import d4_model_count


class DDNNFConfigurationsNumber(ConfigurationsNumber):
    """Exact number of valid configurations, computed by the d4 d-DNNF compiler.

    d4 compiles the CNF to a d-DNNF and counts its models exactly. It scales to large models
    where OBDD compilation (the bdd plugin) can blow up, and unlike the sharpsat plugin the
    result is exact rather than approximate.
    """

    def __init__(self) -> None:
        self._result = 0

    def get_configurations_number(self) -> int:
        return self._result

    def get_result(self) -> int:
        return self._result

    def execute(self, model: VariabilityModel) -> 'DDNNFConfigurationsNumber':
        dnnf_model = cast(DDNNFModel, model)
        self._result = d4_model_count(dnnf_model.dimacs_path)
        return self
