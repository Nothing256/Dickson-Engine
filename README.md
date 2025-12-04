# Dickson-Engine

**A Structural Approach via Dickson Polynomials for Factorization over $\mathbb{Z}_{p^e}*

> A lightweight, deterministic engine implementing the explicit factorization algorithm described in our paper "Explicit Factorization of x^(p+1)-1 over Zpe".

## Features

- **Structural Lifting**: Bypasses generic Hensel lifting using the (x)$ auxiliary polynomial.
- **Scalar Recurrence**: Reduces polynomial arithmetic to simple integer scalar operations.
- **Linear Complexity**: (e \cdot p)$ vs traditional (e^2 \cdot \text{poly}(p))$.

## Architecture

- **Core**: Pure C implementation (C99). Currently uses native 64-bit arithmetic for maximum portability and speed in standard ranges.
- **Benchmark**: Python suite to compare performance against NTL (Number Theory Library).

## Roadmap

- [ ] Implement V(x) generation logic
- [ ] Implement Scalar Lifting Loop
- [ ] Add NTL comparison wrapper
- [ ] **Future**: GMP integration for cryptographic-scale integers (^{1000}+$)

## License

MIT
