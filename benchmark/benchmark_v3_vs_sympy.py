#!/usr/bin/env python3
"""
Benchmark: Dickson Engine V3 vs SymPy (CAS Baseline)
This script demonstrates the capability of V3 to factor ramified polynomials
over Z_{p^e} compared to a standard CAS (SymPy), which crashes due to zero divisors.
"""

import sys
import os
import time

# Add python directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
from dickson_v3 import dickson_v3_full_pipeline

try:
    import sympy
    from sympy.polys.polytools import factor
    from sympy.polys.polyerrors import NotInvertible
except ImportError:
    print("Please install sympy to run this benchmark: pip install sympy")
    sys.exit(1)

def benchmark_v3(p, e, n):
    start = time.perf_counter()
    factors = dickson_v3_full_pipeline(p, e, n)
    elapsed = time.perf_counter() - start
    return len(factors), elapsed

def benchmark_sympy(p, e, n):
    x = sympy.Symbol("x")
    f = x**n - 1
    modulus = p**e
    start = time.perf_counter()
    try:
        factors = factor(f, modulus=modulus)
        elapsed = time.perf_counter() - start
        # If it miraculously works, count the factors
        if isinstance(factors, sympy.Mul):
            count = len(factors.args)
        else:
            count = 1
        return count, elapsed, "Success"
    except NotInvertible as err:
        return 0, 0.0, f"CRASH: {err.__class__.__name__} ({err})"
    except Exception as err:
        return 0, 0.0, f"CRASH: {err.__class__.__name__} ({err})"

def run_benchmarks():
    print("===================================================================")
    print("       Dickson Engine V3 vs SymPy Benchmark (Ramified Cases)       ")
    print("===================================================================")
    print(f"{'n (p=3, e=2)':<15} | {'Dickson V3 (Time)':<20} | {'SymPy Built-in (Result)':<30}")
    print("-" * 68)
    
    p = 3
    e = 2
    test_cases = [12, 24, 36, 72, 108]
    
    for n in test_cases:
        # Run V3
        v3_count, v3_time = benchmark_v3(p, e, n)
        v3_str = f"{v3_time:.6f}s ({v3_count} factors)"
        
        # Run SymPy
        sym_count, sym_time, sym_status = benchmark_sympy(p, e, n)
        if "CRASH" in sym_status:
            sym_str = "\033[91m" + sym_status + "\033[0m" # Red color for crash
        else:
            sym_str = f"{sym_time:.6f}s ({sym_count} factors)"
            
        print(f"n = {n:<11} | {v3_str:<20} | {sym_str:<30}")

if __name__ == "__main__":
    run_benchmarks()
