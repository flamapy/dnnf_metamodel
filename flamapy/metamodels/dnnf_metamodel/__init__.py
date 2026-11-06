import os
import shutil

from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel, MinorLevel

# d-DNNF compilation scales further than BDDs for counting. The cost is a placeholder: the
# 2026-11-06 calibration machine had no d4, so this plugin is the one without measured curves.
# d4 is a native binary with no PyPI distribution (see models.locate_d4): without it the
# transformation fails, so the manifest declares the plugin unavailable and the planner
# never routes to it.
_D4 = os.environ.get('FLAMAPY_D4_PATH') or shutil.which('d4')
_D4_AVAILABLE = _D4 is not None and os.path.exists(_D4)

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
