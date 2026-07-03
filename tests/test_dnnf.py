"""Tests for the d-DNNF (d4) metamodel.

d4 is a native binary with no PyPI distribution, so these tests are skipped unless d4 is
available (on PATH or via FLAMAPY_D4_PATH). When present, exact counts are checked against an
oracle brute-forced from fm_metamodel's solver-agnostic ClauseSet (no SAT plugin needed).
"""
import os
import shutil
import tempfile
from itertools import product

import pytest

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.fm_metamodel.models import FeatureModel, ClauseSet
from flamapy.metamodels.dnnf_metamodel.transformations import FmToDDNNF
from flamapy.metamodels.dnnf_metamodel.operations import (
    DDNNFConfigurationsNumber,
    DDNNFSatisfiable,
)


def _exact_count(fm: FeatureModel) -> int:
    """Exact configuration count by brute-forcing the ClauseSet CNF (no SAT backend)."""
    clause_set = ClauseSet.from_feature_model(fm)
    name_of = {vid: name for name, vid in clause_set.variables.items()}
    var_ids = sorted({abs(lit) for clause in clause_set.clauses for lit in clause}
                     | set(clause_set.variables.values()))
    configs = set()
    for bits in product((False, True), repeat=len(var_ids)):
        assignment = dict(zip(var_ids, bits))
        if all(any((lit > 0) == assignment[abs(lit)] for lit in clause)
               for clause in clause_set.clauses):
            configs.add(frozenset(name_of[v] for v in var_ids if assignment[v] and v in name_of))
    return len(configs)

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
    exact = _exact_count(fm)
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
