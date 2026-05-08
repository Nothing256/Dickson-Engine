#!/usr/bin/env sage
"""
SageMath Benchmark: Factor X^n - 1 over Z_{p^e}

Usage: sage sage_bench.sage <p> <e> <n>

This script uses SageMath's built-in polynomial factorization over
quotient rings Z/(p^e)Z. It serves as the "general-purpose CAS" baseline
for comparison against the Dickson Engine V3.

Output (machine-parseable):
    Factor Count : <count>
    Time Elapsed : <seconds>
"""
import sys
import time

def factor_xn_minus_1_sage(p, e, n):
    """Factor X^n - 1 over Z/(p^e)Z using SageMath."""
    mod = p**e
    R = Zmod(mod)
    S.<x> = R[]
    f = x**n - 1

    start = time.time()
    factors = f.factor()
    elapsed = time.time() - start

    factor_count = sum(1 for _ in factors)
    return factor_count, elapsed

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: sage sage_bench.sage <p> <e> <n>")
        sys.exit(1)

    p = int(sys.argv[1])
    e = int(sys.argv[2])
    n = int(sys.argv[3])

    count, elapsed = factor_xn_minus_1_sage(p, e, n)

    print(f"Factor Count : {count}")
    print(f"Time Elapsed : {elapsed:.6f}")
