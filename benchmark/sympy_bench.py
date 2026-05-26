#!/usr/bin/env python3
"""SymPy Benchmark: Factor X^n - 1 over GF(p)
Usage: python3 sympy_bench.py <p> <e> <n>
Output: Time Elapsed : <seconds>
"""
import sys
import time
from sympy.polys.galoistools import gf_factor
from sympy.polys.domains import ZZ

def factor_xn_minus_1_sympy(p, e, n):
    coeffs = [0] * (n + 1)
    coeffs[0] = 1
    coeffs[n] = (-1) % p
    start = time.time()
    factors = gf_factor(coeffs, p, ZZ)
    elapsed = time.time() - start
    lc, factor_list = factors
    return len(factor_list), elapsed

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 sympy_bench.py <p> <e> <n>")
        sys.exit(1)
    p, e, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    count, elapsed = factor_xn_minus_1_sympy(p, e, n)
    print(f"Factor Count : {count}")
    print(f"Time Elapsed : {elapsed:.6f}")
