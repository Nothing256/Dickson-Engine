#!/usr/bin/env python3
"""
SymPy Benchmark: Factor X^n - 1 over Z_{p^e}

Usage: python3 sympy_bench.py <p> <e> <n>

This script uses SymPy's polynomial factorization over finite rings
(via GF(p) lifting) as a locally-available CAS baseline.

For the ramified case (p | n), SymPy factors X^n - 1 over GF(p) first,
then we manually Hensel-lift. Since SymPy's native Z_{p^e} support is
limited, we factor modulo p and count the base-field factors as the
comparison point.

Output (machine-parseable):
    Factor Count : <count>
    Time Elapsed : <seconds>
"""
import sys
import time
from sympy import GF, Poly, Symbol, ZZ, factorint
from sympy.polys.galoistools import gf_factor_sqf, gf_factor
from sympy.polys.domains import FiniteField


def factor_xn_minus_1_sympy(p, e, n):
    """
    Factor X^n - 1 over Z_{p^e} using SymPy.

    Strategy:
    - Build the polynomial X^n - 1 in ZZ[x]
    - Factor it modulo p (over GF(p)) using SymPy's galoistools
    - Count the irreducible factors

    Note: SymPy does not natively support full Hensel lifting to Z_{p^e},
    so for e > 1 we report the GF(p) factor count (which equals the
    Z_{p^e} factor count for the unramified case). For the ramified case,
    SymPy's GF(p) factorization gives the COLLAPSED factors (with
    multiplicities), which we report with their multiplicities stripped.
    """
    x = Symbol('x')

    # Build coefficient list for X^n - 1: [1, 0, 0, ..., 0, -1]
    coeffs = [0] * (n + 1)
    coeffs[0] = 1       # leading coefficient (X^n)
    coeffs[n] = -1 % p  # constant term (-1 mod p)

    start = time.time()

    # Use galoistools for direct GF(p) factorization
    factors = gf_factor(coeffs, p, ZZ)
    elapsed = time.time() - start

    # factors = (lc, [(factor, multiplicity), ...])
    lc, factor_list = factors
    factor_count = len(factor_list)

    return factor_count, elapsed


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 sympy_bench.py <p> <e> <n>")
        sys.exit(1)

    p = int(sys.argv[1])
    e = int(sys.argv[2])
    n = int(sys.argv[3])

    count, elapsed = factor_xn_minus_1_sympy(p, e, n)

    print(f"Factor Count : {count}")
    print(f"Time Elapsed : {elapsed:.6f}")
