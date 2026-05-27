#!/usr/bin/env python3
"""Exp2 Benchmark Runner: Ring Factorization Z_{p^e} — Medium Parameters
Fixed p=101, n=102, m=2, vary e from 1 to 200.
Three contestants: Dickson V1 (auto) vs V2 (auto) vs SageMath.
"""
import sys
import os
import json
import time
import subprocess
import re

# ── Path Setup ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'python'))

from dickson_v1 import dickson_v1_full_pipeline, dickson_v1_find_seed
from dickson_v2 import dickson_v2_full_pipeline, dickson_v2_find_primitive_seed

# ── Parameters ──────────────────────────────────────────────────────────────
P = 101
N = 102        # p + 1
M = 2
E_VALUES = [1, 2, 3, 5, 10, 20, 50, 100, 200]
ITERATIONS = 10
TIMEOUT = 600  # 10 minutes per single Sage run

# ── Helpers ─────────────────────────────────────────────────────────────────

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


def run_v1(p, e, seed):
    """Run V1 pipeline. Returns elapsed time or None on failure."""
    try:
        elapsed, _ = dickson_v1_full_pipeline(p, e, seed)
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
    """Run SageMath benchmark via subprocess. Returns elapsed time or None."""
    sage_script = os.path.join(SCRIPT_DIR, 'sage_bench.sage')
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


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  Exp2 Benchmark: Ring Medium — V1 vs V2 vs SageMath")
    print(f"  p={P}, n={N}, m={M}, iterations={ITERATIONS}")
    print("=" * 70)

    # ── Pre-compute seeds (NOT timed) ───────────────────────────────────
    print("\n[INIT] Finding V1 seed (auto-seeder)...")
    v1_seed = dickson_v1_find_seed(P)
    print(f"[INIT] V1 seed: A = {v1_seed}")

    print("[INIT] Finding V2 seed (auto-seeder)...")
    v2_seed = dickson_v2_find_primitive_seed(P, M, N)
    print(f"[INIT] V2 seed: G(x) = {v2_seed}")

    # ── Check Sage availability ─────────────────────────────────────────
    sage_available = True
    try:
        subprocess.run(['sage', '--version'], capture_output=True, timeout=10)
    except Exception:
        sage_available = False
        print("[INIT] WARNING: SageMath not found. Skipping Sage benchmarks.")

    # ── Results accumulator ─────────────────────────────────────────────
    results = {
        "experiment": "ring_medium_vary_e",
        "p": P,
        "n": N,
        "m": M,
        "iterations": ITERATIONS,
        "v1_seed": v1_seed,
        "v2_seed": v2_seed,
        "e_values": {},
    }

    # ── Benchmark loop ──────────────────────────────────────────────────
    for e in E_VALUES:
        print(f"\n{'=' * 50}")
        print(f"  e = {e}  (mod = {P}^{e})")
        print(f"{'=' * 50}")

        entry = {"v1": None, "v2": None, "sage": None}

        # --- V1 ---
        print(f"  [V1] Running {ITERATIONS} iterations...")
        v1_times = []
        for i in range(ITERATIONS):
            t = run_v1(P, e, v1_seed)
            v1_times.append(t)
            status = f"{t:.4f}s" if t is not None else "FAILED"
            print(f"    e={e} V1 iter {i + 1}: {status}")
        entry["v1"] = trimmed_mean(v1_times)
        if entry["v1"] is not None:
            print(f"  [V1] trimmed mean = {entry['v1']:.6f}s")

        # --- V2 ---
        print(f"  [V2] Running {ITERATIONS} iterations...")
        v2_times = []
        for i in range(ITERATIONS):
            t = run_v2(P, e, M, v2_seed, N)
            v2_times.append(t)
            status = f"{t:.4f}s" if t is not None else "FAILED"
            print(f"    e={e} V2 iter {i + 1}: {status}")
        entry["v2"] = trimmed_mean(v2_times)
        if entry["v2"] is not None:
            print(f"  [V2] trimmed mean = {entry['v2']:.6f}s")

        # --- SageMath ---
        if sage_available:
            print(f"  [Sage] Running {ITERATIONS} iterations...")
            sage_times = []
            for i in range(ITERATIONS):
                t = run_sage(P, e, N)
                sage_times.append(t)
                status = f"{t:.4f}s" if t is not None else "FAILED"
                print(f"    e={e} Sage iter {i + 1}: {status}")
            entry["sage"] = trimmed_mean(sage_times)
            if entry["sage"] is not None:
                print(f"  [Sage] trimmed mean = {entry['sage']:.6f}s")

        results["e_values"][str(e)] = entry

    # ── Save JSON ───────────────────────────────────────────────────────
    json_path = os.path.join(SCRIPT_DIR, "ring_medium_vary_e.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n[Done] Results saved to {json_path}")


if __name__ == "__main__":
    main()
