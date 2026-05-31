# Dickson-Engine V2

**A Deterministic Multi-Dimensional Algebraic Engine for Factorization over $\mathbb{Z}_{p^e}$**

> A mathematical engine implementing the explicit factorization of cyclotomic polynomials via generalized Multi-Dimensional Dickson Recurrences and MED (Multiple Equal-Difference) cosets.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build: CMake](https://img.shields.io/badge/Build-CMake-green.svg)](https://cmake.org/)

<p align="center">
  <img src="assets/Dickson-Engine-Banner.png" alt="Dickson-Engine Banner" width="800"/>
</p>

## 📚 Academic Lineage & Versions

The Dickson Engine is built to scale homomorphic and post-quantum cryptographic primitives, evolving from the initial 1-dimensional recurrence equations to a complete multi-dimensional tensor-free algebraic framework.

| Version | Key Innovation | Repository Branch/Tag |
|---------|----------------|------------------------|
| **V1.0** (ISIT) | Introduced structural 1D approach via Dickson Polynomials for the $n=p+1$ singularity. | `[tag: v1.0-isit]` |
| **V2.0** (Current) | General Multi-dimensional Recurrences, MED Partitions, Cofactor-Free Hensel Lift, and $O(m^3 \log p)$ Auto-Seeding. Grand total: $O(n + m^3 \log p + e \cdot m^2)$. | `[branch: main]` |

> **Note:** The `main` branch tracks the cutting-edge **V2** engine. If you are looking to reproduce the legacy benchmark results and LCD code constructions from the **V1** paper, please checkout the `v1.0-isit` tag!

## ✨ Features

- **Grand Total Algebraic Complexity**: $O(n + m^3 \log p + e \cdot m^2)$ for the complete factorization of $X^n-1$ over $\mathbb{Z}_{p^e}$, where $n$ is the cyclotomic order, $m$ is the coset dimension, $p$ is the prime, and $e$ is the precision depth.
- **Cofactor-Free Hensel Lifting**: Lifts a single irreducible seed polynomial from $\mathbb{F}_p$ to $\mathbb{Z}_{p^e}$ using a cached polynomial inverse $C(X) = [H(X)]^{-1} \bmod G_1(X)$ computed once over $\mathbb{F}_p$, achieving $O(m^2)$ cost per precision layer—completely bypassing multivariable Jacobian matrix inversions and cofactor updates.
- **Trace Extraction (Power Sums)**: Reduces complex multi-dimensional roots to a pure 1-dimensional integer trace sequence using Newton-Girard identities and the Dickson LFSR recurrence.
- **MED Coset Partitioning**: Extracts all irreducible factors by mathematically scaling and partitioning a single base trace sequence, with degenerate coset handling for mixed-degree decompositions.
- **$O(m^3 \log p)$ Auto-Seeding**: Finds a primitive irreducible seed via randomized primitivity testing in $\mathbb{F}_{p^m}$, where each test requires $O(m \log p)$ multiplications at $O(m^2)$ cost each.
- **Dual-Track Coefficient Reconstruction**: 
  - **Primary Track (Newton-Girard)**: $O(m)$ per factor for standard fields where $p > m$.
  - **Fallback Track (Quotient-Ring Gaussian Elimination)**: $O(m^2 \cdot m)$ per factor for small characteristic ($p \le m$), ensuring unconditional correctness without zero-divisor failures.
- **Pure C99 Engine (Base Field / Small Rings)**: Ultra-lightweight and highly optimized. No external math libraries required. However, native C99 lacks arbitrary-precision arithmetic, limiting its capacity for extremely large precision depths ($e \gg 1$).
- **Pure Python Engine (Large Rings / Bignum)**: A full implementation of the V1 and V2 engines in Python. Leveraging Python's native bignum support, this engine effortlessly handles cryptographically large rings (e.g., $e=1000$). Remarkably, the pure Python V2 engine outperforms industrial-grade C-backed libraries like SageMath and SymPy by orders of magnitude (445× over SageMath at $p=199$).

## 🚀 Quick Start

The Dickson Engine provides both a highly optimized C implementation for base fields and a pure Python implementation for massive ring lifting.

### C Engine Compilation

```bash
mkdir build && cd build
cmake ..
make dickson_bench
```

### Usage

The core benchmark binary executes the Auto-Seeder, dynamically generates traces, and outputs the full factorization of $X^n-1$ over $\mathbb{Z}_{p^e}$.

```bash
# ./bin/dickson_bench <p> <e> <n> [--random]
# Example: Factor X^14 - 1 over Z_{169} (p=13, e=2)
./bin/dickson_bench 13 2 14 --random

# Example: Factor X^39007 - 1 over GF(197)
./bin/dickson_bench 197 1 39007 --random
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `p` | Prime characteristic of the base field |
| `e` | Precision exponent ($e=1$ for $\mathbb{F}_p$, $e \ge 2$ for $\mathbb{Z}_{p^e}$) |
| `n` | Cyclotomic order ($X^n - 1$), must satisfy $\gcd(n, p) = 1$ |
| `--random` | Use the runtime Auto-Seeder instead of precomputed seeds |

### Python Bignum Engine

The Python engine is located in the `python/` directory and features comprehensive benchmarking scripts in `benchmark/`. To witness the V2 engine factor polynomials over massive rings (e.g., $\mathbb{Z}_{p^{1000}}$) and compare its performance against SymPy and SageMath:

```bash
# Run the large ring benchmark (e.g., p=30011, e up to 1000)
python3 benchmark/runner_exp3_ring_large.py
```

#### General Usage & API

The Python engine can be run directly from the command line to factor an arbitrary cyclotomic polynomial $X^n-1$ over $\mathbb{Z}_{p^e}$:

```bash
# Usage: python3 python/dickson_v2.py <p> <e> <n>
# Example: Factor X^14 - 1 over Z_{169} (p=13, e=2, n=14)
python3 python/dickson_v2.py 13 2 14
```

When integrating the engine as a library, it delivers factorization results in two distinct formats:

1. **Machine-Readable API**: The core `dickson_v2_full_pipeline` returns a native Python `list` of coefficient lists (from lowest to highest degree), perfect for downstream programmatic consumption.
2. **SageMath-Style String**: The utility `format_factorization` converts the coefficient arrays into a standard multiplied polynomial string (e.g., `(x^2 + 130x + 168) * ...`), visually identical to standard CAS output.

**Example Python API Usage:**
```python
import sys
sys.path.append('./python')
from dickson_v2 import dickson_v2_full_pipeline, dickson_v2_find_primitive_seed
from poly_arith import format_factorization

p, e, n = 13, 2, 14

# 1. Generate primitive seed (Auto-Seeder)
seed = dickson_v2_find_primitive_seed(p, n)

# 2. Execute V2 Pipeline
elapsed, factors = dickson_v2_full_pipeline(p, e, seed, n)

# 3. Output formats
print("Raw API Output:", factors)
print("SageMath Style:", format_factorization(factors, mod=p**e))
```

## 🔧 Seed Management (Oxygen Tank)

The engine features a **dual-mode** seeding architecture:

1. **Precomputed Seeds** — A lookup table in `core/src/primes_seeds.c` provides pre-verified primitive irreducible polynomials for a curated set of primes. These enable instant startup with zero search overhead.
2. **Runtime Auto-Seeder** (`--random`) — When a precomputed seed is unavailable (or `--random` is specified), the engine dynamically searches for a primitive seed via randomized primitivity testing with algebraic cost $O(m^3 \log p)$.

### Expanding the Seed Table

The precomputed seed table ships with coverage for a selected set of primes ($p \le 200$ and select large primes). To expand the table for your own research needs:

```bash
# 1. Build the Oxygen Tank Generator
cd build && make oxy_tank

# 2. Edit the max_p parameter in benchmark/oxygen_tank_generator.c
#    (line 29: poly_int max_p = 200; -> your desired upper bound)

# 3. Run the generator to regenerate primes_seeds.c
cd benchmark && ../build/bin/oxy_tank

# 4. Rebuild the engine to link the expanded seed table
cd ../build && make dickson_bench
```

> **Tip:** On a powerful server, you can safely increase `max_p` to 10000+ to pre-generate a comprehensive seed arsenal. For primes not in the table, the `--random` Auto-Seeder will always work as a fallback.

## 🧪 Advanced Verification & Benchmarks

Our rigorous mathematical framework provides independent verification and performance plotting.

### 1. Algebraic Verification (`verify.py`)

To prove that our trace sequence intrinsically holds the complete factorization of $X^n-1$, we run a symbolic validation using Sympy. This script reads the traces from the C engine, performs MED coset sampling, and mathematically verifies that the product of reconstructed factors equals $X^n-1$ over $GF(p)$.

```bash
python3 benchmark/verify.py
```

### 2. Comparative Benchmarks (Python Suite)

A graphical benchmarking suite comparing the pure Python Dickson V2 Engine against industrial-grade C-backed Computer Algebra Systems (SageMath and SymPy).

```bash
# Exp 1: Base field scaling (Fixed ord_n(p) = 3, varying p)
python3 benchmark/runner_exp1_domain_vary_p.py

# Exp 2: Medium ring scaling (Fixed p=101, varying e)
python3 benchmark/runner_exp2_ring_medium.py

# Exp 3: Massive ring limit testing (Fixed p=30011, varying e up to 1000)
python3 benchmark/runner_exp3_ring_large.py
```
*Outputs performance metrics and plots to `benchmark/results/`, visually demonstrating the up to 890x execution speedup of V2 over SageMath on large domains, and its unique capability to factor over massive composite rings.*



- [x] **Core**: $m$-dimensional Generalized Recurrence Framework.
- [x] **Seeding**: $O(\log n)$ cyclotomic integrity checks.
- [x] **Lifting**: Jacobian-Free Algebraic Seed Lift from $\mathbb{F}_p$ to $\mathbb{Z}_{p^e}$.
- [x] **Reconstruction**: Full factor output via MED + Newton-Girard.
- [x] **Verification**: MED Coset Trace Scaling & Sympy validation.
- [ ] **The "Abyss"**: Resolving the non-coprime theoretical singularity when $p \mid n$.
- [x] **Small Characteristic**: Division-Free Multivariate Generation (Matrix-based) bypassing Newton-Girard singularities when $p \le m$.
- [ ] **Parallelism**: Multi-threaded trace extraction (The "Wolf Pack" strategy).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built with ❤️ by the Dickson Team of <b>Phoenix Universe</b>. Mathematics is absolute.</i>
</p>
