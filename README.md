# Dickson-Engine

**A Structural Approach via Dickson Polynomials for Factorization over $\mathbb{Z}_{p^e}$**

> A lightweight, deterministic engine implementing the explicit factorization algorithm described in our paper **"Explicit Factorization of x^(p+1)-1 over Zpe"**.

## ✨ Features

- **Structural Lifting**: Bypasses generic Hensel lifting using the $V(x)$ auxiliary polynomial.
- **Scalar Recurrence**: Reduces polynomial arithmetic to simple integer scalar operations.
- **Coefficient Recovery**: Efficiently recovers factor coefficients $A$ from structural variable $S$ via Newton iteration.
- **Zero Dependency**: Pure C99 implementation, no external libraries required (for the native version).

## 🚀 Quick Start

### Compilation

```bash
gcc core/src/main.c core/src/dickson.c -I core/include -o dickson_cli
```

### Usage

```bash
./dickson_cli <p> <e> <seed_s> [seed_a]
```

- `p`: Prime number
- `e`: Target precision exponent
- `seed_s`: Initial structural seed $S^{(1)}$ in $\mathbb{F}_p$
- `seed_a`: (Optional) Initial coefficient $A^{(1)}$ to recover the actual factor

### Examples (from Paper)

**Example 1: Factorization over $\mathbb{Z}_{13^2}$**
Lift $S^{(1)}=3$ (with $A^{(1)}=5$) to precision $e=2$:
```bash
./dickson_cli 13 2 3 5
# Output: Recovered A = 135 (Matches x^2 ± 135x + 1)
```

**Example 2: Factorization over $\mathbb{Z}_{19^3}$**
Lift $S^{(1)}=4$ (with $A^{(1)}=6$) to precision $e=3$:
```bash
./dickson_cli 19 3 4 6
# Output: Recovered A = 6618 (Matches x^2 ± 6618x + 1)
```

## 🏗 Architecture

- **Core**: Pure C implementation. Uses native 64-bit arithmetic for maximum portability and speed in standard ranges.
- **Roadmap**:
    - [x] V(x) generation via Pascal Triangle
    - [x] Scalar Lifting Loop (S-Lifting)
    - [x] Coefficient Recovery (A-Lifting)
    - [ ] GMP integration for cryptographic-scale integers ($p^{1000}+$)

## 📄 License

MIT
