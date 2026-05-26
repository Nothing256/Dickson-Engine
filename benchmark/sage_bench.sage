#!/usr/bin/env sage
"""SageMath Benchmark: Factor X^n - 1 over Z/{p^e}Z
Usage: sage sage_bench.sage <p> <e> <n>
Output: Time Elapsed : <seconds>
"""
import sys
import time

def factor_xn_minus_1_sage(p, e, n):
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
    p, e, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    count, elapsed = factor_xn_minus_1_sage(p, e, n)
    print(f"Factor Count : {count}")
    print(f"Time Elapsed : {elapsed:.6f}")
