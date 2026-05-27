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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
    fig.subplots_adjust(hspace=0.3)

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

    # log(p) fit on V2 precomputed
    if len(p_v2_pre) >= 3:
        log_p = [math.log2(p) for p in p_v2_pre]
        log_p_arr = np.array(log_p)
        v2_arr = np.array(v2_pre)
        c_fit = np.sum(v2_arr * log_p_arr) / np.sum(log_p_arr ** 2)
        p_fit = np.linspace(min(p_v2_pre), max(p_v2_pre), 100)
        t_fit = c_fit * np.log2(p_fit)
        ax1.plot(p_fit, t_fit, 'k--', linewidth=1.5, alpha=0.5,
                 label=f'Best fit: {c_fit:.4f} · log₂(p)')

    ax1.legend(fontsize=11, loc='upper left')

    # Bottom: V2(precomp) time / log(p)
    if len(p_v2_pre) >= 3:
        log_p = [math.log2(p) for p in p_v2_pre]
        normalized = [t / lp for t, lp in zip(v2_pre, log_p)]

        ax2.plot(p_v2_pre, normalized, 'b-s', linewidth=2, markersize=7,
                 label='V2(precomp) / log₂(p)')

        ax2.set_xlabel('Prime Characteristic (p)', fontsize=12)
        ax2.set_ylabel('Time / log₂(p)', fontsize=12)
        ax2.set_title('Complexity Verification: V2 Time Normalized by log₂(p)',
                      fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend(fontsize=11)

    # Save
    for ext in ['png', 'pdf']:
        save_path = os.path.join(out_dir, f'domain_vary_p.{ext}')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved to {out_dir}/domain_vary_p.png/.pdf")
    plt.close()


if __name__ == '__main__':
    main()
