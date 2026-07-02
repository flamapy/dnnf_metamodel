# flamapy-dnnf

`flamapy-dnnf` is a [flamapy](https://flamapy.github.io) plugin for **exact** analysis of feature
models via **d-DNNF knowledge compilation**, using the [d4](https://github.com/crillab/d4) compiler.

d-DNNF (deterministic Decomposable Negation Normal Form) is a highly succinct compilation target
that supports exact, polytime model counting. It complements the ecosystem:

- `flamapy-bdd` — OBDD; exact, but can blow up on large models.
- `flamapy-sdd` — SDD; exact, more succinct than OBDD, pure-Python (PySDD).
- `flamapy-sharpsat` — ApproxMC; **approximate** count for very large models.
- `flamapy-dnnf` — d4/d-DNNF; **exact** count that scales to large industrial models.

## Requirements

d4 is a native C++ binary with **no PyPI package**. Install it from
<https://github.com/crillab/d4> and either put it on your `PATH` as `d4` or point
`FLAMAPY_D4_PATH` at the binary.

```
pip install flamapy-dnnf
export FLAMAPY_D4_PATH=/path/to/d4   # or have `d4` on PATH
```

## Operations

| Operation | Class |
|---|---|
| Exact number of configurations | `DDNNFConfigurationsNumber` |
| Satisfiable (non-void) | `DDNNFSatisfiable` |

## Usage

```python
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.dnnf_metamodel.transformations import FmToDDNNF
from flamapy.metamodels.dnnf_metamodel.operations import DDNNFConfigurationsNumber

fm = UVLReader('model.uvl').transform()
dnnf_model = FmToDDNNF(fm).transform()          # add compile=True to also dump the d-DNNF file
count = DDNNFConfigurationsNumber().execute(dnnf_model).get_result()
```

## License

GPL-3.0-or-later.
