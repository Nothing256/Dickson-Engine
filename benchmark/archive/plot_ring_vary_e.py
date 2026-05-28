import json
import matplotlib.pyplot as plt
import os

RESULTS_DIR = "results"

def load_json(filename):
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def main():
    v1_data = load_json("ring_vary_e_v1.json")
    v2_data = load_json("ring_vary_e_v2.json")
    
    if not v1_data or not v2_data:
        print("Error: Missing JSON data files. Please run both V1 and V2 benchmarks first.")
        return
        
    e_values = sorted([int(e) for e in v1_data.keys()])
    
    v1_times = [v1_data[str(e)] for e in e_values]
    v2_times = [v2_data[str(e)] for e in e_values]
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(e_values, v1_times, 'r-o', linewidth=2, markersize=6, label='Dickson V1 (Trace Recurrence) O(p)')
    plt.plot(e_values, v2_times, 'b--s', linewidth=2, markersize=6, label='Dickson V2 (Precomputed Seed) O(log p)')
    
    plt.title('Ring Lifting Time vs Target Precision (e) at fixed p=30011', fontsize=14)
    plt.xlabel('Precision Level (e)', fontsize=12)
    plt.ylabel('Time Elapsed (seconds)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Use logarithmic scale if the gap is huge
    # plt.yscale('log')
    
    out_png = os.path.join(RESULTS_DIR, "ring_lifting_vary_e.png")
    out_pdf = os.path.join(RESULTS_DIR, "ring_lifting_vary_e.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    
    print(f"Plots saved to {out_png} and {out_pdf}")

if __name__ == "__main__":
    main()
