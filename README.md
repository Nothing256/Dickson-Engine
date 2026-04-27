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
| **V2.0** (Current) | General Multi-dimensional Recurrences, MED Partitions, and $O(\log n)$ Auto-Seeding bypass. | `[branch: main]` |

> **Note:** The `main` branch tracks the cutting-edge **V2** engine. If you are looking to reproduce the legacy benchmark results and LCD code constructions from the **V1** paper, please checkout the `v1.0-isit` tag!

## ✨ Features

- **Jacobian-Free Algebraic Lifting**: Lifts irreducible seed polynomials from $\mathbb{F}_p$ to $\mathbb{Z}_{p^e}$ using a structurally isolated remainder congruence $E(X) \equiv \Delta G(X) \cdot H(X) \pmod{G(X)}$, completely bypassing multivariable Jacobian matrix inversions.
- **Trace Extraction (Power Sums)**: Reduces complex multi-dimensional roots to a pure 1-dimensional integer trace sequence using Newton-Girard identities.
- **MED Coset Partitioning**: Extracts all irreducible factors by mathematically scaling and partitioning a single base trace sequence.
- **O(log n) Auto-Seeding**: Dramatically drops the primitive seed search complexity from NTL's $O(p^4)$ to $O(m^2 \log n)$ via rapid cyclotomic norm checking.
- **Full Factor Reconstruction**: Directly outputs the complete factorization of $X^n-1$ as explicit polynomial coefficients over $\mathbb{Z}_{p^e}$.
- **Pure C99 Implementation**: Ultra-lightweight and highly optimized. No external math libraries required.

## 🚀 Quick Start

### Compilation

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

## 🔧 Seed Management (Oxygen Tank)

The engine features a **dual-mode** seeding architecture:

1. **Precomputed Seeds** — A lookup table in `core/src/primes_seeds.c` provides pre-verified primitive irreducible polynomials for a curated set of primes. These enable instant startup with zero search overhead.
2. **Runtime Auto-Seeder** (`--random`) — When a precomputed seed is unavailable (or `--random` is specified), the engine dynamically searches for a primitive seed using $O(\log n)$ cyclotomic integrity checks.

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

### 2. Triple Threat Benchmark (`runner_random_compare.py`)

A graphical benchmarking suite comparing the Dickson Engine (Auto-Seed & Precomputed) against the leading Number Theory Library (NTL).

```bash
python3 benchmark/runner_random_compare.py
```
*Renders a logarithmic performance graph in `benchmark/results/`, visually demonstrating the million-fold $O(p^4)$ vs $O(\log p)$ execution speedup.*

## ⚠️ Known Limitations

### Small Characteristic Singularity ($p \le m$)

When the field characteristic $p$ is less than or equal to the coset dimension $m$ (the multiplicative order of $p$ modulo $n$), the Newton-Girard identities require division by integers $k$ where $1 \le k \le m$. If $p \mid k$, this division is non-invertible over $\mathbb{Z}_{p^e}$, creating an **algebraic singularity**.

In such cases, the engine will:
- ✅ Correctly generate the full trace sequence $T[1], \ldots, T[n]$
- ✅ Correctly perform the Jacobian-Free Algebraic Lift to $\mathbb{Z}_{p^e}$
- ❌ Report `[Degenerate Coset]` for factors whose reconstruction requires the singular division

**Example:** $p=2, e=3, n=7$ ($m=3$). The engine successfully lifts the seed to $X^3+6X^2+5X+7$ over $\mathbb{Z}_8$, but cannot reconstruct the factor coefficients from traces because $\text{inv}(2) \pmod{8}$ does not exist.

> This is a fundamental mathematical boundary, not a software bug. Resolving this singularity is an active area of investigation (see Roadmap).

## 🗺️ Roadmap

- [x] **Core**: $m$-dimensional Generalized Recurrence Framework.
- [x] **Seeding**: $O(\log n)$ cyclotomic integrity checks.
- [x] **Lifting**: Jacobian-Free Algebraic Seed Lift from $\mathbb{F}_p$ to $\mathbb{Z}_{p^e}$.
- [x] **Reconstruction**: Full factor output via MED + Newton-Girard.
- [x] **Verification**: MED Coset Trace Scaling & Sympy validation.
- [ ] **The "Abyss"**: Resolving the non-coprime theoretical singularity when $p \mid n$.
- [ ] **Small Characteristic**: Hensel-lifting Newton-Girard into $\mathbb{Z}_{p^e}$ where $p^e > m$.
- [ ] **Parallelism**: Multi-threaded trace extraction (The "Wolf Pack" strategy).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built with ❤️ by the Dickson Team of <b>Phoenix Universe</b>. Mathematics is absolute.</i>
</p>
