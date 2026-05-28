#!/usr/bin/env python3
"""Plot four-way benchmark results for vary_e experiment."""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

def main():
    json_path = os.path.join(RESULTS_DIR, "ring_vary_e_bignum.json")
    with open(json_path) as f:
        data = json.load(f)

    p = data["p"]
    sympy_baseline = data.get("sympy_baseline_e1")

    e_vals = []
    v1_times = []
    v2_times = []
    sage_times = []

    for e_str, entry in sorted(data["e_values"].items(), key=lambda x: int(x[0])):
        e = int(e_str)
        e_vals.append(e)
        v1_times.append(entry.get("v1"))
        v2_times.append(entry.get("v2"))
        sage_times.append(entry.get("sage"))

    fig, ax = plt.subplots(figsize=(12, 7))

    # Filter None values for plotting
    def plot_line(xs, ys, **kwargs):
        valid = [(x, y) for x, y in zip(xs, ys) if y is not None]
        if valid:
            vx, vy = zip(*valid)
            ax.plot(vx, vy, **kwargs)

    plot_line(e_vals, v1_times, color='#DC2626', marker='o', linewidth=2, markersize=7,
             label='Dickson V1 (Scalar Lift) O(e·p)', linestyle='-')
    plot_line(e_vals, v2_times, color='#2563EB', marker='s', linewidth=2, markersize=7,
             label='Dickson V2 (Algebraic Lift) O(e·log p)', linestyle='--')
    plot_line(e_vals, sage_times, color='#059669', marker='^', linewidth=2, markersize=7,
             label='SageMath (FLINT/Pari)', linestyle=':')

    if sympy_baseline is not None:
        ax.axhline(y=sympy_baseline, color='#9CA3AF', linestyle='-.', linewidth=1.5,
                   label=f'SymPy GF(p) baseline (e=1): {sympy_baseline:.3f}s')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Precision Level (e)', fontsize=13)
    ax.set_ylabel('Time Elapsed (seconds)', fontsize=13)
    ax.set_title(f'Ring Factorization Time vs Precision Level (e) at p={p}', fontsize=14)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    png_path = os.path.join(RESULTS_DIR, 'ring_lifting_vary_e_bignum.png')
    pdf_path = os.path.join(RESULTS_DIR, 'ring_lifting_vary_e_bignum.pdf')
    plt.savefig(png_path, dpi=200)
    plt.savefig(pdf_path)
    print(f"[Plot] Saved to {png_path} and {pdf_path}")
    plt.close()

if __name__ == "__main__":
    main()
