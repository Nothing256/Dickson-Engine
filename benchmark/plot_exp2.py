#!/usr/bin/env python3
"""
Plot Exp2: Ring Factorization Z_{101^e}, n=102 — Vary e
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
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, 'ring_medium_vary_e.json')
    out_dir = os.path.dirname(json_path)

    data = load_data(json_path)
    results = data['e_values']
    p = data['p']

    e_vals = sorted(int(k) for k in results.keys())
    v1_t, v2_t, sage_t = [], [], []
    e_v1, e_v2, e_sage = [], [], []

    for e in e_vals:
        r = results[str(e)]
        if r.get('v1') is not None:
            v1_t.append(r['v1'])
            e_v1.append(e)
        if r.get('v2') is not None:
            v2_t.append(r['v2'])
            e_v2.append(e)
        if r.get('sage') is not None:
            sage_t.append(r['sage'])
            e_sage.append(e)

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(e_v1, v1_t, 'r-o', linewidth=2, markersize=7,
            label=f'Dickson V1 (Scalar Lift)')
    ax.plot(e_v2, v2_t, 'b--s', linewidth=2, markersize=7,
            label=f'Dickson V2 (Cofactor-Free Lift)')
    if sage_t:
        ax.plot(e_sage, sage_t, 'g:^', linewidth=2, markersize=8,
                label='SageMath (FLINT/Pari)')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Precision Level (e)', fontsize=12)
    ax.set_ylabel('Time Elapsed (seconds)', fontsize=12)
    ax.set_title(f'Ring Factorization: $X^{{{p+1}}} - 1$ over $\\mathbb{{Z}}_{{{p}^e}}$',
                 fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(fontsize=12)

    # Annotate Sage failure point in the middle blank area
    if e_sage and max(e_sage) < max(e_vals):
        last_sage_e = max(e_sage)
        # Position annotation in the center-right blank area of the chart
        ax.annotate(f'SageMath:\ne > {last_sage_e} not supported',
                    xy=(last_sage_e, sage_t[-1]),
                    xytext=(20, 0.003),
                    fontsize=11, color='green', fontweight='bold',
                    ha='center',
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

    for ext in ['png', 'pdf']:
        save_path = os.path.join(out_dir, f'ring_medium_vary_e.{ext}')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved to {out_dir}/ring_medium_vary_e.png/.pdf")
    plt.close()


if __name__ == '__main__':
    main()
