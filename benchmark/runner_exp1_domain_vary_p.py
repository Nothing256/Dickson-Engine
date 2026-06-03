#!/usr/bin/env python3
"""
Exp1 Benchmark Runner — Domain Factorization over GF(p), e=1
============================================================
For each prime p, computes n = p^2 + p + 1 and benchmarks four contestants:
  1. V2 (precomputed seed)
  2. V2 (auto-seeder)
  3. SageMath   (subprocess)
  4. SymPy      (subprocess)

Results are saved to ring_domain_vary_p.json in the script's directory.
"""

import sys
import os
import time
import json
import subprocess

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'python'))

from dickson_v2 import (
    get_precomputed_seed,
    dickson_v2_full_pipeline,
    dickson_v2_find_primitive_seed,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 47, 53, 59, 61, 67,
    71, 79, 83, 89, 97, 101, 107, 113, 127, 131, 137, 139, 149, 151, 157,
    163, 167, 173, 179, 181, 191, 193, 197, 199,
]

ITERATIONS = 10
TIMEOUT = 600  # seconds


# ---------------------------------------------------------------------------
# Trimmed mean: drop min & max when we have >= 5 samples
# ---------------------------------------------------------------------------
def trimmed_mean(times):
    """Return trimmed mean of *times* (drop min/max if >= 5 values)."""
    valid = [t for t in times if t is not None]
    if not valid:
        return None
    if len(valid) >= 5:
        valid = sorted(valid)
        valid = valid[1:-1]  # drop min and max
    return sum(valid) / len(valid)


# ---------------------------------------------------------------------------
# Contestant 1 — V2 (precomputed seed)
# ---------------------------------------------------------------------------
def bench_v2_precomputed(p, e, m, n, iteration):
    seed = get_precomputed_seed(p, m)
    if seed is None:
        print(f"  p={p} V2(pre) iter {iteration}: no precomputed seed")
        return None
    t0 = time.perf_counter()
    dickson_v2_full_pipeline(p, e, seed, n)
    elapsed = time.perf_counter() - t0
    print(f"  p={p} V2(pre) iter {iteration}: {elapsed:.4f}s")
    return elapsed


# ---------------------------------------------------------------------------
# Contestant 2 — V2 (auto-seeder)
# ---------------------------------------------------------------------------
def bench_v2_auto(p, e, n, iteration):
    t0 = time.perf_counter()
    seed = dickson_v2_find_primitive_seed(p, n)
    dickson_v2_full_pipeline(p, e, seed, n)
    elapsed = time.perf_counter() - t0
    print(f"  p={p} V2(auto) iter {iteration}: {elapsed:.4f}s")
    return elapsed


# ---------------------------------------------------------------------------
# Contestant 3 — SageMath (subprocess)
# ---------------------------------------------------------------------------
def bench_sage(p, e, n, iteration):
    sage_script = os.path.join(SCRIPT_DIR, 'sage_bench_gfp.sage')
    try:
        result = subprocess.run(
            ['sage', sage_script, str(p), str(e), str(n)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        for line in result.stdout.splitlines():
            if 'Time Elapsed' in line:
                # Expected format: "Time Elapsed : X.XXXXXX"
                elapsed = float(line.split(':')[-1].strip())
                print(f"  p={p} Sage iter {iteration}: {elapsed:.4f}s")
                return elapsed
        print(f"  p={p} Sage iter {iteration}: could not parse output")
        if result.stderr.strip():
            print(f"    stderr: {result.stderr.strip()[:200]}")
        return None
    except FileNotFoundError:
        print(f"  p={p} Sage iter {iteration}: sage not installed")
        return None
    except subprocess.TimeoutExpired:
        print(f"  p={p} Sage iter {iteration}: TIMEOUT ({TIMEOUT}s)")
        return None
    except Exception as exc:
        print(f"  p={p} Sage iter {iteration}: ERROR {exc}")
        return None


# ---------------------------------------------------------------------------
# Contestant 4 — SymPy (subprocess)
# ---------------------------------------------------------------------------
def bench_sympy(p, e, n, iteration):
    sympy_script = os.path.join(SCRIPT_DIR, 'sympy_bench.py')
    try:
        result = subprocess.run(
            [sys.executable, sympy_script, str(p), str(e), str(n)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        for line in result.stdout.splitlines():
            if 'Time Elapsed' in line:
                elapsed = float(line.split(':')[-1].strip())
                print(f"  p={p} SymPy iter {iteration}: {elapsed:.4f}s")
                return elapsed
        print(f"  p={p} SymPy iter {iteration}: could not parse output")
        if result.stderr.strip():
            print(f"    stderr: {result.stderr.strip()[:200]}")
        return None
    except FileNotFoundError:
        print(f"  p={p} SymPy iter {iteration}: python/sympy not found")
        return None
    except subprocess.TimeoutExpired:
        print(f"  p={p} SymPy iter {iteration}: TIMEOUT ({TIMEOUT}s)")
        return None
    except Exception as exc:
        print(f"  p={p} SymPy iter {iteration}: ERROR {exc}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    e = 1
    m = 3
    results = {}

    print("=" * 60)
    print("Exp1: Domain Factorization — vary p, e=1, n=p²+p+1")
    print(f"Primes: {len(PRIMES)},  Iterations: {ITERATIONS}")
    print("=" * 60)

    for p in PRIMES:
        n = p ** 2 + p + 1
        print(f"\n--- p={p}, n={n} ---")

        times_pre = []
        times_auto = []
        times_sage = []
        

        for i in range(1, ITERATIONS + 1):
            times_pre.append(bench_v2_precomputed(p, e, m, n, i))
            times_auto.append(bench_v2_auto(p, e, n, i))
            times_sage.append(bench_sage(p, e, n, i))
            

        results[str(p)] = {
            'v2_precomp': trimmed_mean(times_pre),
            'v2_auto':    trimmed_mean(times_auto),
            'sage':       trimmed_mean(times_sage),
            
        }

        print(f"  => means: pre={results[str(p)]['v2_precomp']}, "
              f"auto={results[str(p)]['v2_auto']}, "
              f"sage={results[str(p)]['sage']}, "
              "")

    # -----------------------------------------------------------------------
    # Save JSON
    # -----------------------------------------------------------------------
    output = {
        'experiment': 'domain_vary_p',
        'n_formula':  'p^2+p+1',
        'm': m,
        'e': e,
        'iterations': ITERATIONS,
        'results': results,
    }
    out_path = os.path.join(SCRIPT_DIR, 'ring_domain_vary_p.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
