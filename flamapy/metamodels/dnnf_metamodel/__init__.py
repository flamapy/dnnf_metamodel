from flamapy.core.exceptions import FlamaException
from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel, MinorLevel
from flamapy.metamodels.dnnf_metamodel.models.dnnf_model import locate_d4

# d-DNNF compilation scales further than BDDs for counting. The cost is a placeholder: the
# 2026-11-06 calibration machine had no d4, so this plugin is the one without measured curves.
# It declares no ``calibration``, so the planner only picks it when no calibrated plugin can
# run the operation.
# d4 is a native binary with no PyPI distribution (see models.locate_d4): without it the
# operations fail (the transformation, which only writes the DIMACS file, still runs), so the
# manifest declares the plugin unavailable and the planner never routes to it. The check runs
# once, when the plugin is imported: set FLAMAPY_D4_PATH before that.


def _d4_available() -> bool:
    try:
        locate_d4()
    except FlamaException:
        return False
    return True


_D4_AVAILABLE = _d4_available()

MANIFEST = PluginManifest(
    name='dnnf',
    extension='dnnf',
    available=_D4_AVAILABLE,
    unavailable_reason='the d4 compiler is not installed (set FLAMAPY_D4_PATH or put d4 on PATH)',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY}),
    operations={
        'configurations_number': OperationCapability(cost=80),
    },
)
