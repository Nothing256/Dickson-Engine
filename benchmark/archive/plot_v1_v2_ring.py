import os
import re
import matplotlib.pyplot as plt

def parse_logs(prefix, iterations=10):
    data = {}
    for i in range(1, iterations + 1):
        filename = f"{prefix}_{i}.txt"
        if not os.path.exists(filename):
            continue
        with open(filename, 'r') as f:
            content = f.read()
            matches = re.findall(r"e=(\d+)\s+\|\s+Time:\s+([0-9\.]+)s", content)
            for m in matches:
                e = int(m[0])
                time = float(m[1])
                if e not in data:
                    data[e] = []
                data[e].append(time)
    
    # Compute averages dropping min/max
    averages = {}
    for e, times in data.items():
        if len(times) >= 5:
            times.remove(max(times))
            times.remove(min(times))
        elif len(times) >= 3:
            times.remove(max(times))
            times.remove(min(times))
            
        averages[e] = sum(times) / len(times)
        
    # return sorted lists
    sorted_es = sorted(averages.keys())
    sorted_times = [averages[e] for e in sorted_es]
    return sorted_es, sorted_times

v1_es, v1_times = parse_logs("log_v1_ring")
v2_es, v2_times = parse_logs("log_v2_ring")

plt.figure(figsize=(10, 6))
plt.plot(v1_es, v1_times, 'r-o', linewidth=2, markersize=8, label='Dickson V1 (Algebraic Lift O(e))')
plt.plot(v2_es, v2_times, 'b--s', linewidth=2, markersize=8, label='Dickson V2 (Homogeneous Track O(1))')

plt.title('Benchmark: Dickson V1 vs V2 over Z_{p^e} (p=30011)', fontsize=14)
plt.xlabel('Precision Layer (e)', fontsize=12)
plt.ylabel('Time Elapsed (seconds)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)

# Set y-axis to start from 0 to clearly show the flatline of V2 vs the scaling of V1
plt.ylim(bottom=0)

os.makedirs("results", exist_ok=True)
save_path = "results/v1_vs_v2_ring_comparison.png"
plt.savefig(save_path)
print(f"Graph saved to '{save_path}'")
