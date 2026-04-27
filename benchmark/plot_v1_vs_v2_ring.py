import os
import re
import matplotlib.pyplot as plt

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def parse_log(filepath):
    e_values = []
    times = []
    with open(filepath, 'r') as f:
        for line in f:
            match = re.search(r"e=(\d+).*?Time[:=]\s*(\d+\.\d+)", line)
            if match:
                e_values.append(int(match.group(1)))
                times.append(float(match.group(2)))
    return e_values, times

def main():
    log_v1_opts = ["log_v1_ring.txt"]
    log_v2_opts = ["log_v2_ring.txt"]

    log_v1 = next((p for p in log_v1_opts if os.path.exists(p)), None)
    log_v2 = next((p for p in log_v2_opts if os.path.exists(p)), None)

    if not log_v1 or not log_v2:
        print("Required log files not found. Please run the benchmark runners first.")
        return

    e1, t1 = parse_log(log_v1)
    e2, t2 = parse_log(log_v2)

    plt.figure(figsize=(10, 6))
    
    # 画图：V1 vs V2 的 e 扩展曲线
    plt.plot(e1, t1, 'r-o', linewidth=2, markersize=8, label='V1 Engine (V(x) Array Construction + Jacobian Inverse)')
    plt.plot(e2, t2, 'b-^', linewidth=2, markersize=8, label='V2 Engine (Jacobian-Free Remainder Extraction)')

    plt.title('Performance Across Lifting Precisions (p=30011, Base Ring = Z_{p^e})', fontsize=14)
    plt.xlabel('Precision Level e (approaching Z_{p^e})', fontsize=12)
    plt.ylabel('Time Elapsed (seconds)', fontsize=12)
    
    # 因为这两条线的耗时相差了几十倍，但都是 O(e) 的直线，
    # 在普通坐标系下看也非常震撼，V2 就贴着 x 轴
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)

    # 标注倍数差距
    if len(e1) > 0 and len(e2) > 0:
        ratio = t1[-1] / t2[-1]
        plt.annotate(f"{ratio:.1f}x Faster\nat e={e1[-1]}", 
                     xy=(e2[-1], t2[-1]), xytext=(e2[-1]-200, t2[-1]+0.02),
                     arrowprops=dict(facecolor='black', shrink=0.05),
                     fontsize=12, fontweight='bold')

    save_path = os.path.join(RESULTS_DIR, "v1_vs_v2_ring_scaling.png")
    plt.savefig(save_path)
    print(f"[Success] Plot generated and saved to {save_path}")

if __name__ == "__main__":
    main()
