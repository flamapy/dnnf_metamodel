import re
import subprocess

from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.dnnf_metamodel.models import locate_d4

# d4 prints the exact model count on a solution line, e.g. "s 1904"; the count is unbounded so
# it is parsed as an arbitrary-precision Python int.
_COUNT_LINE = re.compile(r'^s\s+(\d+)\s*$', re.MULTILINE)


def d4_model_count(dimacs_path: str) -> int:
    """Run d4 in exact model-counting mode over a DIMACS file and return the count."""
    d4 = locate_d4()
    completed = subprocess.run(
        [d4, dimacs_path, '-mc'],
        check=True, capture_output=True, text=True,
    )
    match = _COUNT_LINE.search(completed.stdout)
    if match is None:
        raise FlamaException(f'Could not parse a model count from d4 output:\n{completed.stdout}')
    return int(match.group(1))
