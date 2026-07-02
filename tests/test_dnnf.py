"""Tests for the d-DNNF (d4) metamodel.

d4 is a native binary with no PyPI distribution, so these tests are skipped unless d4 is
available (on PATH or via FLAMAPY_D4_PATH). When present, exact counts are checked against the
SAT backend oracle.
"""
import os
import shutil
import tempfile

import pytest

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.dnnf_metamodel.transformations import FmToDDNNF
from flamapy.metamodels.dnnf_metamodel.operations import (
    DDNNFConfigurationsNumber,
    DDNNFSatisfiable,
)
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations_number import (
    PySATConfigurationsNumber,
)

_D4_AVAILABLE = bool(os.environ.get('FLAMAPY_D4_PATH') or shutil.which('d4'))
requires_d4 = pytest.mark.skipif(not _D4_AVAILABLE, reason='the d4 compiler is not installed')

_UVL = """features
    Root {abstract}
        mandatory
            Base
        optional
            A
            B
            C
constraints
    A => B
    A | B
"""


def _fm(uvl):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(uvl)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


@requires_d4
def test_count_matches_sat():
    fm = _fm(_UVL)
    exact = PySATConfigurationsNumber().execute(FmToPysat(fm).transform()).get_result()
    dnnf = DDNNFConfigurationsNumber().execute(FmToDDNNF(fm).transform()).get_result()
    assert dnnf == exact


@requires_d4
def test_satisfiable():
    assert DDNNFSatisfiable().execute(FmToDDNNF(_fm(_UVL)).transform()).get_result() is True


def test_transformation_writes_dimacs():
    """The DIMACS export does not need d4 and can always be checked."""
    model = FmToDDNNF(_fm(_UVL)).transform()
    assert os.path.exists(model.dimacs_path)
    with open(model.dimacs_path) as dimacs:
        header = dimacs.readline()
    assert header.startswith('p cnf ')
    assert model.var_count >= 5  # Root, Base, A, B, C
