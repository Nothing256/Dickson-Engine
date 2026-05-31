#!/usr/bin/env python3
"""
Plot Exp1: Domain Factorization GF(p), n=p^2+p+1 — Vary p
With SymPy overlay from backup log data.
"""
import json
import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# SymPy data extracted from exp1_log_backup_05272138.txt (p=2..101, trimmed means)
SYMPY_DATA = {
    2: 0.0001285,
    3: 0.00040625,
    5: 0.001745125,
    7: 0.0059045,
    11: 0.03545175,
    13: 0.059063125,
    17: 0.1686935,
    19: 0.29937325,
    23: 0.73120075,
    29: 1.979418375,
    31: 2.850895875,
    37: 5.758302875,
    41: 9.0645525,
    47: 18.900902,
    53: 30.5405593,
    59: 51.953404,
    61: 59.090415,
    67: 86.852452,
    71: 113.816015,
    79: 201.396375,
    83: 221.299178,
    89: 313.331002,
    97: 480.167015,
    101: 508.200319,
}


def load_data(json_path):
    with open(json_path) as f:
        return json.load(f)


def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, 'ring_domain_vary_p.json')
    out_dir = os.path.dirname(json_path)

    data = load_data(json_path)
    results = data['results']

    # Extract data series
    primes = sorted(int(k) for k in results.keys())
    v2_pre, v2_auto, sage_t = [], [], []
    p_v2_pre, p_v2_auto, p_sage = [], [], []

    for p in primes:
        r = results[str(p)]
        if r.get('v2_precomp') is not None:
            v2_pre.append(r['v2_precomp'])
            p_v2_pre.append(p)
        if r.get('v2_auto') is not None:
            v2_auto.append(r['v2_auto'])
            p_v2_auto.append(p)
        if r.get('sage') is not None:
            sage_t.append(r['sage'])
            p_sage.append(p)

    # SymPy series
    p_sympy = sorted(SYMPY_DATA.keys())
    sympy_t = [SYMPY_DATA[p] for p in p_sympy]

    # --- Main plot ---
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), height_ratios=[2, 1, 1])
    fig.subplots_adjust(hspace=0.4)

    # Top: Time vs p (log scale)
    ax1.plot(p_v2_pre, v2_pre, 'b-s', linewidth=2, markersize=7,
             label='Dickson V2 (Precomputed Seed)')
    ax1.plot(p_v2_auto, v2_auto, 'b--^', linewidth=1.5, markersize=6,
             alpha=0.7, label='Dickson V2 (Auto-Seeder)')
    if sage_t:
        ax1.plot(p_sage, sage_t, 'g-o', linewidth=2, markersize=7,
                 label='SageMath (FLINT/Pari)')
    if sympy_t:
        ax1.plot(p_sympy, sympy_t, 'r-D', linewidth=2, markersize=6,
                 label='SymPy (Cantor-Zassenhaus)')

    ax1.set_yscale('log')
    ax1.set_xlabel('Prime Characteristic (p)', fontsize=12)
    ax1.set_ylabel('Time Elapsed (seconds)', fontsize=12)
    ax1.set_title(r'Domain Factorization: $X^{p^2+p+1} - 1$ over $GF(p)$',
                  fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # O(n) fit on V2 precomputed (where n = p^2 + p + 1)
    if len(p_v2_pre) >= 3:
        n_vals = [p**2 + p + 1 for p in p_v2_pre]
        n_arr = np.array(n_vals)
        v2_arr = np.array(v2_pre)
        # Least squares fit: t = c * n => c = sum(t * n) / sum(n^2)
        c_fit = np.sum(v2_arr * n_arr) / np.sum(n_arr ** 2)
        p_fit = np.linspace(min(p_v2_pre), max(p_v2_pre), 100)
        n_fit = p_fit**2 + p_fit + 1
        t_fit = c_fit * n_fit
        ax1.plot(p_fit, t_fit, 'k--', linewidth=1.5, alpha=0.5,
                 label=f'Best fit: $O(n)$ ($c \\cdot n$)')

    ax1.legend(fontsize=11, loc='upper left')

    # Middle: Seed Discovery Time / log(p)
    if len(p_v2_pre) > 0 and len(p_v2_auto) > 0:
        # Match data points
        seed_time = []
        p_seed = []
        for i, p in enumerate(p_v2_auto):
            if p in p_v2_pre:
                idx = p_v2_pre.index(p)
                # Auto - Pre gives the seed discovery overhead
                overhead = max(0, v2_auto[i] - v2_pre[idx])
                seed_time.append(overhead)
                p_seed.append(p)
        
        if len(p_seed) >= 3:
            log_p_seed = [math.log2(p) for p in p_seed]
            normalized_seed = [t / lp for t, lp in zip(seed_time, log_p_seed)]
            ax2.plot(p_seed, normalized_seed, 'c--^', linewidth=2, markersize=7,
                     label='(V2 Auto - Precomp) / log₂(p)')
            
            ax2.set_xlabel('Prime Characteristic (p)', fontsize=12)
            ax2.set_ylabel('Time / log₂(p)', fontsize=12)
            ax2.set_title(r'Seed Discovery Complexity: $O(\log p)$', fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.5)
            ax2.legend(fontsize=11)

    # Bottom: Expansion Time / n
    if len(p_v2_pre) >= 3:
        n_vals = [p**2 + p + 1 for p in p_v2_pre]
        normalized_pre = [t / n for t, n in zip(v2_pre, n_vals)]
        ax3.plot(p_v2_pre, normalized_pre, 'b-s', linewidth=2, markersize=7,
                 label='V2 Precomp / $n$')
        
        ax3.set_xlabel('Prime Characteristic (p)', fontsize=12)
        ax3.set_ylabel('Time / $n$', fontsize=12)
        ax3.set_title('Coefficient Expansion Complexity: $O(n)$ where $n=p^2+p+1$', fontsize=12)
        ax3.grid(True, linestyle='--', alpha=0.5)
        ax3.legend(fontsize=11)

    # Save
    for ext in ['png', 'pdf']:
        save_path = os.path.join(out_dir, f'domain_vary_p.{ext}')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved to {out_dir}/domain_vary_p.png/.pdf")
    plt.close()


if __name__ == '__main__':
    main()
