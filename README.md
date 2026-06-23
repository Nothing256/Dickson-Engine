# Dickson-Engine V3 — The Ramified Regime

**Complete Factorization of $X^n-1$ over $\mathbb{Z}_{p^e}$ for Arbitrary $n$, Including $p \mid n$**

> The V3 engine extends the Dickson Engine to conquer the "Abyss" — the non-coprime singularity where $p \mid n$. Using the Cyclotomic Substitution Theorem, it achieves closed-form factorization of the ramified regime without Newton polygons, Montes algorithms, or non-coprime Hensel lifting.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build: CMake](https://img.shields.io/badge/Build-CMake-green.svg)](https://cmake.org/)
[![Branch: v3-ramified](https://img.shields.io/badge/Branch-v3--ramified-orange.svg)](#)

<p align="center">
  <img src="assets/Dickson-Engine-Banner.png" alt="Dickson-Engine Banner" width="800"/>
</p>

## 📚 Academic Lineage & Versions

| Version | Key Innovation | Status | Repository Branch/Tag |
|---------|----------------|--------|------------------------|
| **V1.0** | Structural 1D approach via Dickson Polynomials for the $n=p+1$ singularity. | Published at ISIT 2026 | `[tag: v1.0-isit]` |
| **V2.0** | Multi-dimensional Recurrences, MED Partitions, Cofactor-Free Hensel Lift. Unramified case ($\gcd(n,p)=1$). | [arXiv:2606.20633](https://arxiv.org/abs/2606.20633), Under Review | `[branch: main]` |
| **V3.0** ⬅️ | **The Ramified Regime solved.** Cyclotomic Substitution Theorem for *all* $n$, including $p \mid n$. | Under Review | `[branch: v3-ramified]` |

> **You are on the `v3-ramified` branch.** This branch contains the V3 engine that handles the complete factorization including the ramified case. For the V2-only engine, see the `main` branch.

## 🧠 What V3 Solves

When $p \mid n$, writing $n = p^k m$ with $\gcd(m,p)=1$:

$$X^n - 1 = X^{p^k m} - 1 \equiv (X^m - 1)^{p^k} \pmod{p}$$

Every irreducible factor appears with multiplicity $p^k$, causing:
- ❌ Standard Hensel lifting to **fail** (requires coprime factors)
- ❌ SymPy to **crash** with `NotInvertible` (zero divisor)
- ❌ SageMath to **crash** with `PrecisionError` (vanishing discriminant)

The V3 engine solves this via the **Cyclotomic Substitution Theorem**: for each unramified factor $G_i(X)$ of $X^m-1$, the ramified factors are obtained by the closed-form formula:

$$H_i^{(j)}(X) = \frac{G_i(X^{p^j})}{G_i(X^{p^{j-1}})}$$

No Newton polygons. No Montes algorithm. Just polynomial substitution and exact division.

## 🚀 Quick Start

### V3 Python Engine

The V3 engine can be run directly from the command line:

```bash
# Usage: python3 python/dickson_v3.py <p> <e> <n>

# Example 1: Factor X^12 - 1 over Z_9 (p=3, e=2, n=12, ramified: 3 | 12)
python3 python/dickson_v3.py 3 2 12

# Example 2: Factor X^24 - 1 over Z_9 (p=3, e=2, n=24)
python3 python/dickson_v3.py 3 2 24

# Example 3: Factor X^6 - 1 over Z_8 (p=2, e=3, n=6)
python3 python/dickson_v3.py 2 3 6

# Example 4: Unramified case also works (p=13, e=2, n=14, gcd(14,13)=1)
python3 python/dickson_v3.py 13 2 14
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `p` | Prime characteristic |
| `e` | Precision exponent ($e=1$ for $\mathbb{F}_p$, $e \ge 2$ for $\mathbb{Z}_{p^e}$) |
| `n` | Cyclotomic order ($X^n - 1$). **No restriction on $\gcd(n, p)$!** |

### Python API Usage

```python
import sys
sys.path.append('./python')
from dickson_v3 import dickson_v3_full_pipeline
from poly_arith import format_factorization

p, e, n = 3, 2, 12  # Ramified: 3 | 12

# Execute V3 Pipeline (handles both unramified and ramified automatically)
elapsed, factors = dickson_v3_full_pipeline(p, e, n)

# Output
print(f"Time: {elapsed:.6f}s")
print(f"Factors: {len(factors)}")
print(f"Result: {format_factorization(factors, mod=p**e)}")
```

### V2 Engine (Unramified Only)

The V2 engine is still available for unramified cases. See the [main branch README](https://github.com/Nothing256/Dickson-Engine/tree/main) for V2-specific documentation, including C engine compilation, seed management, and the full benchmark suite.

## 🧪 V3 Benchmarks — Reproducing the Paper Results

### 1. Quick Benchmark: V3 vs SymPy (Ramified Crash Demo)

This script demonstrates V3's capability on ramified cases where SymPy crashes:

```bash
python3 benchmark/benchmark_v3_vs_sympy.py
```

**Expected output:**
```
===================================================================
       Dickson Engine V3 vs SymPy Benchmark (Ramified Cases)
===================================================================
n (p=3, e=2)    | Dickson V3 (Time)    | SymPy Built-in (Result)
--------------------------------------------------------------------
n = 12          | 0.000049s (6 factors) | CRASH: NotInvertible (...)
n = 24          | 0.000048s (10 factors)| CRASH: NotInvertible (...)
n = 36          | 0.000038s (9 factors) | CRASH: NotInvertible (...)
n = 72          | 0.000055s (15 factors)| CRASH: NotInvertible (...)
n = 108         | 0.000076s (12 factors)| CRASH: NotInvertible (...)
```

### 2. Full Benchmark Suite (Multi-Axis Sweep)

The comprehensive benchmark runner sweeps across multiple axes:

```bash
python3 benchmark/runner_v3_ramified.py
```

This produces:
- **Sweep A**: Fixed $p=3, e=2$, varying $n = 3m$ for increasing $m$ (scaling with order)
- **Sweep B**: Fixed $n, e$, varying $p$ over small primes (scaling with prime)
- **Plots**: Saved to `results/v3_bench_sweep_n.png` and `results/v3_bench_sweep_p.png`
- **Data**: Saved to `results/v3_bench_data.csv`

### 3. Correctness Verification

Every V3 factorization is self-verifying: the product of all output factors is checked against $X^n - 1 \pmod{p^e}$. This verification is built into the benchmark scripts.

## ✅ Roadmap

- [x] **Core**: $m$-dimensional Generalized Recurrence Framework.
- [x] **Seeding**: $O(\log n)$ cyclotomic integrity checks.
- [x] **Lifting**: Jacobian-Free Algebraic Seed Lift from $\mathbb{F}_p$ to $\mathbb{Z}_{p^e}$.
- [x] **Reconstruction**: Full factor output via MED + Newton-Girard.
- [x] **Verification**: MED Coset Trace Scaling & Sympy validation.
- [x] **The "Abyss" — RESOLVED ✅**: The non-coprime singularity ($p \mid n$) has been conquered by the Cyclotomic Substitution Theorem (V3).
- [x] **Small Characteristic**: Division-Free Multivariate Generation (Matrix-based) bypassing Newton-Girard singularities when $p \le m$.
- [ ] **Parallelism**: Multi-threaded trace extraction (The "Wolf Pack" strategy).
- [ ] **Finite Chain Rings**: Extend framework to Galois rings $\mathrm{GR}(p^e, r)$ and $\mathbb{F}_q[\mu]/(\mu^e)$.

## 📖 Citation

If you find the Dickson Engine useful in your research, we would greatly appreciate it if you could cite our papers:

**Dickson Engine V1** (ISIT 2026 — Published):
```bibtex
@inproceedings{DicksonEngineV1,
  author    = {Yongchao Wang and Yang Ding and Jiansheng Yang and Zhiqiu Huang},
  title     = {Explicit Factorization of $x^{p+1}-1$ over $\mathbb{Z}_{p^e}$: A Structural Approach via Dickson Polynomials},
  booktitle = {Proceedings of the 2026 IEEE International Symposium on Information Theory (ISIT)},
  year      = {2026}
}
```

**Dickson Engine V1 — Extended Version** (arXiv:2604.19038):
```bibtex
@misc{DicksonEngineV1ext,
  title     = {Explicit Factorization of $x^{p+1}-1$ over $\mathbb{Z}_{p^e}$: A Structural Approach via Dickson Polynomials},
  author    = {Yongchao Wang and Yang Ding and Jiansheng Yang and Zhiqiu Huang},
  year      = {2026},
  eprint    = {2604.19038},
  archivePrefix = {arXiv},
  primaryClass  = {cs.IT},
  url       = {https://arxiv.org/abs/2604.19038}
}
```

**Dickson Engine V2** (arXiv:2606.20633 — Under Review):
```bibtex
@misc{DicksonEngineV2,
  title     = {Explicit Factorization of $X^n-1$ over $\mathbb{Z}_{p^e}$ via Cofactor-Free Single-Seed Hensel Lifting},
  author    = {Yongchao Wang and Yang Ding and Jiansheng Yang and Zhiqiu Huang},
  year      = {2026},
  eprint    = {2606.20633},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SC},
  url       = {https://arxiv.org/abs/2606.20633}
}
```

**Dickson Engine V3** (Under Review):
```bibtex
@article{DicksonEngineV3,
  author    = {Yongchao Wang and Yang Ding and Jiansheng Yang and Zhiqiu Huang},
  title     = {Complete Factorization of $X^n-1$ over $\mathbb{Z}_{p^e}$ for Arbitrary $n$: The Ramified Regime via Cyclotomic Substitution},
  year      = {2026},
  note      = {Under Review}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built with ❤️ by the Dickson Team of <b>Phoenix Universe</b>. Mathematics is absolute.</i>
</p>
