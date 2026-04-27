# Dickson-Engine

**A Structural Approach via Dickson Polynomials for Factorization over $\mathbb{Z}_{p^e}$**

> A lightweight, deterministic engine implementing the explicit factorization algorithm described in our paper **"Explicit Factorization of x^(p+1)-1 over Zpe"**.

[![Paper-Link-Placeholder](https://img.shields.io/badge/Paper-Link%20to%20be%20Added-blueviolet)](https://placeholder.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="assets/Dickson-Engine-Banner.png" alt="Dickson-Engine Banner" width="800"/>
</p>

## 📚 Academic Lineage & Versions

The Dickson Engine is being actively developed to scale homomorphic and post-quantum cryptographic primitives. Please refer to the specific branches and tags corresponding to our publications:

| Version | Publication / Venue | Key Innovation | Repository Branch/Tag |
|---------|---------------------|----------------|------------------------|
| **V1.0** (ISIT) | *IEEE International Symposium on Information Theory (ISIT) 2026* | Introduced structural approach via Dickson Polynomials for $n=p+1$ | `[tag: v1.0-isit]` |
| **V2.0** (TIT) | *IEEE Transactions on Information Theory (TIT) [Under Review]* | Multi-dimensional LFSR Auto-Seeding, $O(ep \log n)$ tensor-free bypass for arbitrary dimensions | `[branch: main]` |

> **Note:** The `main` branch tracks the cutting-edge **V2** engine. If you are looking to reproduce the exact benchmark results from the **V1 ISIT** paper, please checkout the `v1.0-isit` tag!



## ✨ Features

- **Structural Lifting**: Bypasses generic Hensel lifting using the $V(x)$ auxiliary polynomial.
- **Scalar Recurrence**: Reduces polynomial arithmetic to simple integer scalar operations.
- **Coefficient Recovery**: Efficiently recovers factor coefficients $A$ from structural variable $S$ via Newton iteration.
- **Zero Dependency**: Pure C99 implementation. No external math libraries required.
- **Verified Accuracy**: Cross-validated against NTL (Number Theory Library) on prime fields.

## 🚀 Quick Start

### Compilation

```bash
mkdir build && cd build
cmake ..
make
```

### Usage

```bash
./bin/dickson_cli <p> <e> [options]
```

**Options:**
- `--auto` : Automatically search for a valid seed (Benchmark mode).
- `--full <seed>` : Generate all factors using a manual seed.
- `--silent` : Suppress factor output (show statistics only).
- `--output <file>` : Write factorization results to a file.

**Example:**
```bash
# Factorize x^20 - 1 over Z_{19^3}
./bin/dickson_cli 19 3 --auto
```

## 🛠️ Applications: Quantum & LCD Code Construction

We provide a powerful, multi-core Python engine to construct and verify codes over $\mathbb{Z}_{p^e}$.

### 1. Quantum/LCD Code Search (`quantum_search.py`)

This script generates cyclic codes from the factors found by the C++ engine, maps them to $\mathbb{F}_p$ via the Gray map, and evaluates their minimum distance $d$.

**Features:**
- **Two Modes**: 
  - `scan`: Massive parallel sampling for high-dimension codes.
  - `brute`: Exhaustive search (Brute-Force) for low-dimension codes (Exact $d$).
- **Traceability**: Records the specific factor combination ("Gene") for every code.
- **Auto-Sniper**: Automatically switches to intensive sampling when a high-quality candidate is found.

**Usage:**

```bash
# Mode A: Massive Sampling (for exploration)
python3 applications/quantum_search.py --mode scan

# Mode B: Brute Force (for proving optimality, e.g., k <= 4)
python3 applications/quantum_search.py --mode brute --k_max 4
```

### 2. Visualization (`visualizer_final.py`)

Generates the "Skyline Plot" comparing our constructed codes against the theoretical Griesmer Bound.

```bash
python3 applications/visualizer_final.py
```
*Output: `lcd_codes_performance.png`*

## 🧪 Advanced Usage: The "Oxygen Tank" & Benchmark Comparisons

When running Dickson experiments on heavy computing clusters (like Ubuntu servers), generating roots dynamically using the Auto-Seeder introduces overhead. Bypassing this requires generating our mathematically pre-checked dictionary of primitive factors (The **Oxygen Tank**).

### Compiling and Generating the Oxygen Tank
This utility spins up the V2 Engine, calculates the primitive seeds for dimension $m=2$ and $m=3$ for primes up to $p=200$ (configurable), and natively writes C-language dictionary mappings directly to `core/src/primes_seeds.c`.

```bash
cd Dickson-Engine/build
make oxy_tank
./bin/oxy_tank
```
*Note: After generating the new `primes_seeds.c`, you MUST run `make` again in the build directory to link your newly built dictionary into the main engine.*

### Triple Threat Benchmark: NTL vs. Auto-Seed vs. Precomputed
To visualize the "Fairness Match" executing our $O(p)$ algorithm against the catastrophic $O(p^4)$ bottleneck created by the **NTL (Number Theory Library) Jacobian Matrix**:

```bash
# Verify all binaries exist
make -C build

# Execute the comparative evaluation: NTL vs. V2 Auto vs. V2 Precomputed
python3 benchmark/runner_v2_random_compare.py
```
*This renders `benchmark/results/v2_triple_comparison.png`, utilizing a logarithmic Y-axis to chart the million-fold performance differential scaling.*

## 📊 Benchmarks

Our engine demonstrates significant performance advantages over standard libraries (NTL):
- **O(p) Complexity**: Linear scaling with prime size $p$, compared to NTL's super-linear growth.
- **Linear Lifting**: Lifting complexity scales linearly with precision $e$.
- **Ring Native**: Performs full ring factorization faster than NTL performs base field factorization.

*(See `benchmark/results/` for detailed graphs generated by `runner.py`)*

## 🗺️ Roadmap

- [x] **Core**: V(x) generation via Pascal Triangle.
- [x] **Lifting**: Scalar Lifting Loop (S-Lifting) & Newton Recovery (A-Lifting).
- [x] **CLI**: Full automation with integrity checks for random seeding.
- [ ] **Parallelism**: Multi-threaded implementation using OpenMP/Pthreads to leverage the independent lifting property (The "Wolf Pack" strategy).
- [ ] **Big Int**: GMP integration for cryptographic-scale integers ($p^{1000}+$).

## Citation

If you find our work useful in your research, we would be grateful if you could cite our paper:

```bibtex
TBD
```
