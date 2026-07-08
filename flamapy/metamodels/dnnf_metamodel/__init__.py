from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

# d-DNNF compilation scales further than BDDs for counting; cost placeholder to be
# refined from benchmark calibration data.
MANIFEST = PluginManifest(
    name='dnnf',
    extension='dnnf',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
    operations={
        'configurations_number': OperationCapability(cost=80),
    },
)
