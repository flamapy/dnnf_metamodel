import os
import shutil
from typing import Optional

from flamapy.core.models import VariabilityModel
from flamapy.core.exceptions import FlamaException


def locate_d4() -> str:
    """Return the path to the d4 compiler binary.

    Resolved from the ``FLAMAPY_D4_PATH`` environment variable, or ``d4`` on ``PATH``. d4 is a
    native C++ binary (https://github.com/crillab/d4) with no PyPI distribution, so it must be
    installed separately.
    """
    candidate = os.environ.get('FLAMAPY_D4_PATH') or shutil.which('d4')
    if not candidate or not os.path.exists(candidate):
        raise FlamaException(
            'The d4 compiler was not found. Install d4 (https://github.com/crillab/d4) and '
            'expose it as "d4" on PATH or via the FLAMAPY_D4_PATH environment variable.'
        )
    return candidate


class DDNNFModel(VariabilityModel):
    """A d-DNNF (deterministic Decomposable Negation Normal Form) view of a feature model.

    The model keeps the CNF (as DIMACS) produced from the feature model; exact queries are
    answered by the external d4 compiler, which compiles the CNF to d-DNNF internally. The
    compiled d-DNNF artifact can optionally be dumped to ``nnf_path``.
    """

    @staticmethod
    def get_extension() -> str:
        return 'dnnf'

    def __init__(self) -> None:
        self.dimacs_path: str = ''             # path to the CNF in DIMACS format
        self.nnf_path: Optional[str] = None    # optional compiled d-DNNF artifact
        self.var_count: int = 0
        self.variables: dict[str, int] = {}    # feature name -> DIMACS variable index
        self.features: dict[int, str] = {}     # DIMACS variable index -> feature name
        self.original_model: Optional[VariabilityModel] = None

    def feature_variables(self) -> list[int]:
        return list(self.features.keys())
