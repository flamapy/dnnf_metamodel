import os
import subprocess
import tempfile

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.dnnf_metamodel.models import DDNNFModel, locate_d4


class FmToDDNNF(ModelToModel):
    """Transform a feature model into a d-DNNF-backed model.

    Builds the CNF (reusing the SAT metamodel), writes it as DIMACS, and — when ``compile`` is
    set — invokes d4 to dump the compiled d-DNNF artifact. Exact queries run d4 on the DIMACS.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'dnnf'

    def __init__(
        self,
        source_model: FeatureModel,
        cnf_method: str = 'distributive',
        compile: bool = False,
    ) -> None:
        self.source_model = source_model
        self.cnf_method = cnf_method
        self.compile = compile
        self.destination_model = DDNNFModel()

    def transform(self) -> DDNNFModel:
        if self.cnf_method == 'distributive':
            sat_model = FmToPysat(self.source_model).transform()
        else:
            sat_model = FmToPysat(self.source_model, cnf_method=self.cnf_method).transform()

        clauses = [list(clause) for clause in sat_model.get_all_clauses().clauses]
        var_count = max((abs(literal) for clause in clauses for literal in clause), default=1)

        dimacs_fd, dimacs_path = tempfile.mkstemp(suffix='.cnf', prefix='flamapy_dnnf_')
        with os.fdopen(dimacs_fd, 'w') as dimacs_file:
            dimacs_file.write(f'p cnf {var_count} {len(clauses)}\n')
            for clause in clauses:
                dimacs_file.write(' '.join(str(literal) for literal in clause) + ' 0\n')

        model = self.destination_model
        model.dimacs_path = dimacs_path
        model.var_count = var_count
        model.variables = dict(sat_model.variables)
        model.features = dict(sat_model.features)
        model.original_model = self.source_model

        if self.compile:
            nnf_fd, nnf_path = tempfile.mkstemp(suffix='.nnf', prefix='flamapy_dnnf_')
            os.close(nnf_fd)
            d4 = locate_d4()
            # d4 compiles the CNF to a d-DNNF and dumps it to nnf_path.
            subprocess.run(
                [d4, dimacs_path, '-dDNNF', f'-out={nnf_path}'],
                check=True, capture_output=True, text=True,
            )
            model.nnf_path = nnf_path

        return model
