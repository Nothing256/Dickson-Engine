#!/usr/bin/env python3
"""
Dickson Engine V3 — Ramified Regime Benchmark Runner

This script compares the Dickson V3 engine against SymPy (local) and
optionally SageMath (if available) for factoring X^n - 1 over Z_{p^e}
in the RAMIFIED regime (p | n).

Benchmark Axes:
  A) Fixed p, e: sweep n = p * m for increasing m  (scaling with order)
  B) Fixed n, e: sweep p over small primes          (scaling with prime)
  C) Fixed p, n: sweep e = 1, 2, 3, ...             (scaling with precision)

Usage: python3 runner_v3_ramified.py

Outputs:
  - results/v3_bench_sweep_n.png
  - results/v3_bench_sweep_p.png
  - results/v3_bench_data.csv
"""

import subprocess
import os
import re
import csv
import time
import sys

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[WARN] matplotlib not found. Plots will not be generated.")
    print("       Install with: pip3 install matplotlib")

# --- Configuration ---
DICKSON_V3_BIN = "build/bin/dickson_v3_bench"
SYMPY_BENCH = "benchmark/sympy_bench.py"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Check if SageMath is available
SAGE_AVAILABLE = False
try:
    subprocess.run(["sage", "--version"], capture_output=True, timeout=5)
    SAGE_AVAILABLE = True
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass


def run_dickson_v3(p, e, n):
    """Run Dickson V3 benchmark and return (factor_count, elapsed_time)."""
    cmd = [DICKSON_V3_BIN, str(p), str(e), str(n), "--quiet"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=120, check=True)
        count_match = re.search(r"Factor Count\s*:\s*(\d+)", result.stdout)
        time_match = re.search(r"Time Elapsed\s*:\s*([\d.]+)", result.stdout)
        verified_match = re.search(r"Verified\s*:\s*(\w+)", result.stdout)

        count = int(count_match.group(1)) if count_match else -1
        elapsed = float(time_match.group(1)) if time_match else -1.0
        verified = (verified_match.group(1) == "YES") if verified_match else False

        return count, elapsed, verified
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return -1, -1.0, False


def run_sympy(p, e, n):
    """Run SymPy benchmark and return (factor_count, elapsed_time)."""
    cmd = [sys.executable, SYMPY_BENCH, str(p), str(e), str(n)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300, check=True)
        count_match = re.search(r"Factor Count\s*:\s*(\d+)", result.stdout)
        time_match = re.search(r"Time Elapsed\s*:\s*([\d.]+)", result.stdout)

        count = int(count_match.group(1)) if count_match else -1
        elapsed = float(time_match.group(1)) if time_match else -1.0

        return count, elapsed
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return -1, -1.0


def run_sage(p, e, n):
    """Run SageMath benchmark and return (factor_count, elapsed_time)."""
    if not SAGE_AVAILABLE:
        return -1, -1.0
    cmd = ["sage", "benchmark/sage_bench.sage", str(p), str(e), str(n)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300, check=True)
        count_match = re.search(r"Factor Count\s*:\s*(\d+)", result.stdout)
        time_match = re.search(r"Time Elapsed\s*:\s*([\d.]+)", result.stdout)

        count = int(count_match.group(1)) if count_match else -1
        elapsed = float(time_match.group(1)) if time_match else -1.0

        return count, elapsed
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return -1, -1.0


# ============================================================
# Benchmark A: Fixed p=2, e=2, sweep n = 2*m for increasing m
# ============================================================
def bench_sweep_n():
    """Sweep n (order) with fixed p=2, e=2. Tests ramified factorization scaling."""
    p, e = 2, 2
    # m values: coprime to p=2, so odd numbers
    m_values = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 31, 35, 41, 45,
                51, 55, 63, 73, 85, 93, 105, 127, 155, 189, 217, 255]
    n_values = [2 * m for m in m_values]

    results = []
    print("\n" + "=" * 70)
    print(f"  Benchmark A: Sweep n (p={p}, e={e}, n = {p}*m)")
    print("=" * 70)
    print(f"{'n':>8} {'m':>6} | {'Dickson V3':>12} {'SymPy':>12} | {'Speedup':>8} | {'V3 ok':>5}")
    print("-" * 70)

    for m, n in zip(m_values, n_values):
        d_count, d_time, d_verified = run_dickson_v3(p, e, n)
        s_count, s_time = run_sympy(p, e, n)

        speedup = s_time / d_time if d_time > 0 and s_time > 0 else float('inf')

        status = "✓" if d_verified else "✗"
        print(f"{n:>8} {m:>6} | {d_time:>11.6f}s {s_time:>11.6f}s | {speedup:>7.1f}x | {status:>5}")

        results.append({
            'bench': 'sweep_n', 'p': p, 'e': e, 'n': n, 'm': m,
            'dickson_time': d_time, 'dickson_count': d_count, 'dickson_verified': d_verified,
            'sympy_time': s_time, 'sympy_count': s_count, 'speedup': speedup
        })

        # Safety: skip if SymPy already takes > 60s
        if s_time > 60:
            print("  [STOP] SymPy exceeds 60s, truncating sweep.")
            break

    return results


# ============================================================
# Benchmark B: Fixed n formula, sweep primes
# ============================================================
def bench_sweep_p():
    """Sweep p with n = p * (p+1). Tests across different primes."""
    e = 2
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]

    results = []
    print("\n" + "=" * 70)
    print(f"  Benchmark B: Sweep p (e={e}, n = p*(p+1))")
    print("=" * 70)
    print(f"{'p':>5} {'n':>8} | {'Dickson V3':>12} {'SymPy':>12} | {'Speedup':>8} | {'V3 ok':>5}")
    print("-" * 70)

    for p in primes:
        n = p * (p + 1)  # Ensures p | n and m = p+1 which is coprime to p
        d_count, d_time, d_verified = run_dickson_v3(p, e, n)
        s_count, s_time = run_sympy(p, e, n)

        speedup = s_time / d_time if d_time > 0 and s_time > 0 else float('inf')

        status = "✓" if d_verified else "✗"
        print(f"{p:>5} {n:>8} | {d_time:>11.6f}s {s_time:>11.6f}s | {speedup:>7.1f}x | {status:>5}")

        results.append({
            'bench': 'sweep_p', 'p': p, 'e': e, 'n': n, 'm': p + 1,
            'dickson_time': d_time, 'dickson_count': d_count, 'dickson_verified': d_verified,
            'sympy_time': s_time, 'sympy_count': s_count, 'speedup': speedup
        })

        if s_time > 120:
            print("  [STOP] SymPy exceeds 120s, truncating sweep.")
            break

    return results


def save_csv(all_results):
    """Save all benchmark results to CSV."""
    csv_path = os.path.join(RESULTS_DIR, "v3_bench_data.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'bench', 'p', 'e', 'n', 'm',
            'dickson_time', 'dickson_count', 'dickson_verified',
            'sympy_time', 'sympy_count', 'speedup'
        ])
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\n[CSV] Results saved to {csv_path}")


def plot_sweep_n(results):
    """Plot Benchmark A: sweep n."""
    if not HAS_MPL:
        return

    data = [r for r in results if r['bench'] == 'sweep_n'
            and r['dickson_time'] > 0 and r['sympy_time'] > 0]
    if not data:
        return

    ns = [r['n'] for r in data]
    d_times = [r['dickson_time'] for r in data]
    s_times = [r['sympy_time'] for r in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Left: Absolute timing
    ax1.semilogy(ns, d_times, 'b-o', linewidth=2, markersize=6,
                 label='Dickson V3', color='#2563EB')
    ax1.semilogy(ns, s_times, 'r-s', linewidth=2, markersize=6,
                 label='SymPy (gf_factor)', color='#DC2626')
    ax1.set_xlabel('Order n (= 2m, ramified at p=2)', fontsize=12)
    ax1.set_ylabel('Time (seconds, log scale)', fontsize=12)
    ax1.set_title('V3 Ramified Factorization: Scaling with Order n', fontsize=13)
    ax1.legend(fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Right: Speedup ratio
    speedups = [r['speedup'] for r in data]
    ax2.bar(range(len(ns)), speedups, color='#059669', alpha=0.85)
    ax2.set_xticks(range(len(ns)))
    ax2.set_xticklabels([str(n) for n in ns], rotation=45, ha='right', fontsize=8)
    ax2.set_xlabel('Order n', fontsize=12)
    ax2.set_ylabel('Speedup (SymPy / Dickson V3)', fontsize=12)
    ax2.set_title('Speedup Ratio', fontsize=13)
    ax2.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "v3_bench_sweep_n.png")
    plt.savefig(path, dpi=150)
    print(f"[Plot] Sweep-n saved to {path}")
    plt.close()


def plot_sweep_p(results):
    """Plot Benchmark B: sweep p."""
    if not HAS_MPL:
        return

    data = [r for r in results if r['bench'] == 'sweep_p'
            and r['dickson_time'] > 0 and r['sympy_time'] > 0]
    if not data:
        return

    ps = [r['p'] for r in data]
    d_times = [r['dickson_time'] for r in data]
    s_times = [r['sympy_time'] for r in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Left: Absolute timing
    ax1.semilogy(ps, d_times, 'b-o', linewidth=2, markersize=6,
                 label='Dickson V3', color='#2563EB')
    ax1.semilogy(ps, s_times, 'r-s', linewidth=2, markersize=6,
                 label='SymPy (gf_factor)', color='#DC2626')
    ax1.set_xlabel('Prime p (n = p(p+1), ramified)', fontsize=12)
    ax1.set_ylabel('Time (seconds, log scale)', fontsize=12)
    ax1.set_title('V3 Ramified Factorization: Scaling with Prime p', fontsize=13)
    ax1.legend(fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Right: Speedup ratio
    speedups = [r['speedup'] for r in data]
    ax2.bar(range(len(ps)), speedups, color='#7C3AED', alpha=0.85)
    ax2.set_xticks(range(len(ps)))
    ax2.set_xticklabels([str(p) for p in ps], fontsize=9)
    ax2.set_xlabel('Prime p', fontsize=12)
    ax2.set_ylabel('Speedup (SymPy / Dickson V3)', fontsize=12)
    ax2.set_title('Speedup Ratio', fontsize=13)
    ax2.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "v3_bench_sweep_p.png")
    plt.savefig(path, dpi=150)
    print(f"[Plot] Sweep-p saved to {path}")
    plt.close()


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Dickson Engine V3 — Ramified Regime Benchmark Suite    ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if not os.path.exists(DICKSON_V3_BIN):
        print(f"\n[ERROR] Binary not found: {DICKSON_V3_BIN}")
        print("Please build first: cd build && cmake .. && make dickson_v3_bench")
        return

    if SAGE_AVAILABLE:
        print("[INFO] SageMath detected — will include Sage benchmarks.")
    else:
        print("[INFO] SageMath not found — using SymPy as CAS baseline.")

    all_results = []

    # Benchmark A: Sweep n
    results_a = bench_sweep_n()
    all_results.extend(results_a)

    # Benchmark B: Sweep p
    results_b = bench_sweep_p()
    all_results.extend(results_b)

    # Save data
    save_csv(all_results)

    # Generate plots
    plot_sweep_n(all_results)
    plot_sweep_p(all_results)

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║         V3 Benchmark Suite Complete!                     ║")
    print("╚══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
