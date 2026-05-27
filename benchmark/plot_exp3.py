#!/usr/bin/env python3
"""
Plot Exp3: Large-scale Ring Factorization Z_{30011^e} — V1 vs V2
Reads: ring_vary_e_bignum.json (existing overnight data)
Produces: ring_large_vary_e.png / .pdf
"""
import json
import os
import sys
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data(json_path):
    with open(json_path) as f:
        return json.load(f)

def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, 'ring_vary_e_bignum.json')
    out_dir = os.path.dirname(json_path)

    data = load_data(json_path)
    results = data['e_values']
    p = data['p']

    e_vals = sorted(int(k) for k in results.keys())
    v1_t, v2_t = [], []
    e_v1, e_v2 = [], []

    for e in e_vals:
        r = results[str(e)]
        if r.get('v1') is not None:
            v1_t.append(r['v1'])
            e_v1.append(e)
        if r.get('v2') is not None:
            v2_t.append(r['v2'])
            e_v2.append(e)

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(e_v1, v1_t, 'r-o', linewidth=2, markersize=8,
            label=f'Dickson V1 (Scalar Lift) O(e·p)')
    ax.plot(e_v2, v2_t, 'b--s', linewidth=2, markersize=8,
            label=f'Dickson V2 (Algebraic Lift) O(e·log p)')

    # Sage annotation (only had e=1)
    sage_e1 = data['e_values'].get('1', {}).get('sage')
    if sage_e1 is not None:
        ax.plot([1], [sage_e1], 'g^', markersize=12, zorder=5,
                label=f'SageMath (e=1 only): {sage_e1:.1f}s')
        ax.annotate(f'SageMath: {sage_e1:.1f}s\ne≥2: Not Supported',
                    xy=(1, sage_e1),
                    xytext=(3, sage_e1 * 1.5),
                    fontsize=10, color='green',
                    arrowprops=dict(arrowstyle='->', color='green'))

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Precision Level (e)', fontsize=12)
    ax.set_ylabel('Time Elapsed (seconds)', fontsize=12)
    ax.set_title(f'Ring Factorization: $X^{{{p+1}}} - 1$ over $\\mathbb{{Z}}_{{{p}^e}}$ (End-to-End)',
                 fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(fontsize=12, loc='upper left')

    # Speedup annotations at key points
    for e_val in [100, 1000]:
        e_str = str(e_val)
        if e_str in results:
            r = results[e_str]
            if r.get('v1') and r.get('v2'):
                speedup = r['v1'] / r['v2']
                ax.annotate(f'{speedup:.0f}×',
                            xy=(e_val, r['v2']),
                            xytext=(e_val, r['v2'] / 3),
                            fontsize=11, fontweight='bold', color='blue',
                            ha='center',
                            arrowprops=dict(arrowstyle='->', color='blue'))

    for ext in ['png', 'pdf']:
        save_path = os.path.join(out_dir, f'ring_large_vary_e.{ext}')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved to {out_dir}/ring_large_vary_e.png/.pdf")
    plt.close()

if __name__ == '__main__':
    main()
