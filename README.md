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

- **Structural Algebraic Lifting**: Bypasses generic Hensel lifting relying on Euclidean GCDs.
- **Trace Extraction (Power Sums)**: Reduces complex multi-dimensional roots to a pure 1-dimensional integer trace sequence using Newton-Girard identities.
- **MED Coset Partitioning**: Extracts all irreducible factors by mathematically scaling and partitioning a single base trace sequence.
- **O(log n) Auto-Seeding**: Dramatically drops the primitive seed search complexity from NTL's $O(p^4)$ to $O(m^2 \log n)$ via rapid cyclotomic norm checking.
- **Pure C99 Implementation**: Ultra-lightweight and highly optimized. No external math libraries required.

## 🚀 Quick Start

### Compilation

```bash
mkdir build && cd build
cmake ..
make
```

### Usage

The core benchmark binary executes the Auto-Seeder, dynamically generates traces, and outputs performance logs.

```bash
# ./bin/dickson_bench <p> <e> <n> [options]
./bin/dickson_bench 197 1 39007 --random
```

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

## 🗺️ Roadmap

- [x] **Core**: $m$-dimensional Generalized Recurrence Framework.
- [x] **Seeding**: $O(\log n)$ cyclotomic integrity checks.
- [x] **Verification**: MED Coset Trace Scaling & Sympy validation.
- [ ] **The "Abyss"**: Resolving the non-coprime theoretical singularity when $p \mid n$.
- [ ] **Parallelism**: Multi-threaded trace extraction (The "Wolf Pack" strategy).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>Built with ❤️ by the Dickson Team of <b>Phoenix Universe</b>. Mathematics is absolute.</i>
</p>
