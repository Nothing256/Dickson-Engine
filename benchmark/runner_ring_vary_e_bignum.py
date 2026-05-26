#!/usr/bin/env python3
"""Four-Way Benchmark: Dickson V1 vs V2 vs SageMath vs SymPy
Fixed p=30011, vary e from 1 to 1000.
"""
import sys
import os
import json
import time
import subprocess
import re

# Add python/ directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
from dickson_v1 import dickson_v1_full_pipeline, dickson_v1_build_vx, dickson_v1_find_seed
from dickson_v2 import dickson_v2_full_pipeline, get_precomputed_seed

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

P = 30011
N = P + 1  # 30012
M = 2  # multiplicative order of p mod n for n = p+1
E_VALUES = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
ITERATIONS = 10
TIMEOUT = 600  # 10 minutes per single run

def run_v1(p, e, n, v1_seed, v1_coeffs, v1_k):
    """Run V1 pipeline. Returns elapsed time or None on failure."""
    try:
        elapsed, _, _ = dickson_v1_full_pipeline(p, e, v1_seed)
        return elapsed
    except Exception as ex:
        print(f"    V1 error: {ex}")
        return None

def run_v2(p, e, m, seed, n):
    """Run V2 pipeline. Returns elapsed time or None on failure."""
    try:
        elapsed, _ = dickson_v2_full_pipeline(p, e, m, seed, n)
        return elapsed
    except Exception as ex:
        print(f"    V2 error: {ex}")
        return None

def run_sage(p, e, n):
    """Run SageMath benchmark via subprocess."""
    sage_script = os.path.join(os.path.dirname(__file__), 'sage_bench.sage')
    cmd = ['sage', sage_script, str(p), str(e), str(n)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        match = re.search(r'Time Elapsed\s*:\s*(\d+\.\d+)', result.stdout)
        if match:
            return float(match.group(1))
        return None
    except (subprocess.TimeoutExpired, Exception) as ex:
        print(f"    Sage error: {ex}")
        return None

def run_sympy(p, e, n):
    """Run SymPy benchmark via subprocess."""
    sympy_script = os.path.join(os.path.dirname(__file__), 'sympy_bench.py')
    cmd = [sys.executable, sympy_script, str(p), str(e), str(n)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        match = re.search(r'Time Elapsed\s*:\s*(\d+\.\d+)', result.stdout)
        if match:
            return float(match.group(1))
        return None
    except (subprocess.TimeoutExpired, Exception) as ex:
        print(f"    SymPy error: {ex}")
        return None

def trimmed_mean(times):
    """Compute trimmed mean: remove best and worst, average the rest."""
    valid = [t for t in times if t is not None]
    if len(valid) >= 3:
        s = sorted(valid)
        trimmed = s[1:-1]
        return sum(trimmed) / len(trimmed)
    elif valid:
        return sum(valid) / len(valid)
    return None

def main():
    print("=" * 70)
    print("  Four-Way Benchmark: Dickson V1 vs V2 vs SageMath vs SymPy")
    print(f"  Fixed p={P}, n={N}, Iterations={ITERATIONS}")
    print("=" * 70)

    # Pre-compute V1 seed
    print("\n[INIT] Finding V1 seed for p=30011...")
    v1_seed = dickson_v1_find_seed(P)
    print(f"[INIT] V1 seed: A = {v1_seed}")

    # Pre-compute V1 polynomial V(x)
    v1_coeffs, v1_k = dickson_v1_build_vx(P)
    print(f"[INIT] V(x) degree: {v1_k}")

    # Get V2 seed
    v2_seed = get_precomputed_seed(P, M)
    if v2_seed is None:
        print("[INIT] ERROR: No precomputed V2 seed for p=30011!")
        return
    print(f"[INIT] V2 seed: G(x) = {v2_seed}")

    # Check Sage availability
    sage_available = True
    try:
        subprocess.run(['sage', '--version'], capture_output=True, timeout=10)
    except Exception:
        sage_available = False
        print("[INIT] WARNING: SageMath not found. Skipping Sage benchmarks.")

    # Run SymPy once at e=1 as baseline
    print("\n[SYMPY] Running SymPy baseline at e=1...")
    sympy_times = []
    for i in range(ITERATIONS):
        t = run_sympy(P, 1, N)
        sympy_times.append(t)
        if t is not None:
            print(f"  iter {i+1}: {t:.6f}s")
    sympy_baseline = trimmed_mean(sympy_times)
    print(f"  >> SymPy baseline (e=1): {sympy_baseline:.6f}s" if sympy_baseline else "  >> SymPy FAILED")

    results = {
        "p": P, "n": N, "iterations": ITERATIONS,
        "v1_seed": v1_seed,
        "v2_seed": v2_seed,
        "sympy_baseline_e1": sympy_baseline,
        "e_values": {},
    }

    log_path = os.path.join(RESULTS_DIR, "log_runner_ring_vary_e_bignum.txt")
    with open(log_path, "w") as log:
        log.write(f"Four-Way Benchmark: p={P}, n={N}\n")
        log.write(f"V1 seed: {v1_seed}, V2 seed: {v2_seed}\n")
        log.write(f"SymPy baseline (e=1): {sympy_baseline}\n\n")

        for e in E_VALUES:
            print(f"\n{'='*50}")
            print(f"  e = {e}  (mod = {P}^{e})")
            print(f"{'='*50}")

            entry = {"v1": None, "v2": None, "sage": None}

            # --- V1 ---
            print(f"  [V1] Running {ITERATIONS} iterations...")
            v1_times = []
            for i in range(ITERATIONS):
                t = run_v1(P, e, N, v1_seed, v1_coeffs, v1_k)
                v1_times.append(t)
                status = f"{t:.6f}s" if t is not None else "FAILED"
                print(f"    iter {i+1}: {status}")
                log.write(f"e={e} V1 iter {i+1}: {status}\n")
            entry["v1"] = trimmed_mean(v1_times)
            if entry["v1"] is not None:
                print(f"  [V1] mean = {entry['v1']:.6f}s")

            # --- V2 ---
            print(f"  [V2] Running {ITERATIONS} iterations...")
            v2_times = []
            for i in range(ITERATIONS):
                t = run_v2(P, e, M, v2_seed, N)
                v2_times.append(t)
                status = f"{t:.6f}s" if t is not None else "FAILED"
                print(f"    iter {i+1}: {status}")
                log.write(f"e={e} V2 iter {i+1}: {status}\n")
            entry["v2"] = trimmed_mean(v2_times)
            if entry["v2"] is not None:
                print(f"  [V2] mean = {entry['v2']:.6f}s")

            # --- Sage ---
            if sage_available:
                print(f"  [Sage] Running {ITERATIONS} iterations...")
                sage_times = []
                for i in range(ITERATIONS):
                    t = run_sage(P, e, N)
                    sage_times.append(t)
                    status = f"{t:.6f}s" if t is not None else "FAILED"
                    print(f"    iter {i+1}: {status}")
                    log.write(f"e={e} Sage iter {i+1}: {status}\n")
                entry["sage"] = trimmed_mean(sage_times)
                if entry["sage"] is not None:
                    print(f"  [Sage] mean = {entry['sage']:.6f}s")

            results["e_values"][str(e)] = entry
            log.flush()

    # Save JSON
    json_path = os.path.join(RESULTS_DIR, "ring_vary_e_bignum.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n[Done] Results saved to {json_path}")

if __name__ == "__main__":
    main()
