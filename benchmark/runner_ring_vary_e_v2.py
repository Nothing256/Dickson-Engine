import subprocess
import os
import re
import json

DICKSON_BENCH = "build/bin/dickson_bench"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_v2(p, e, n):
    # DO NOT pass --random. This uses the Precomputed Seed (Oxygen Tank)
    # which we specifically generated for p=30011 to isolate lifting time.
    cmd = [DICKSON_BENCH, str(p), str(e), str(n)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        time_match = re.search(r"Time Elapsed\s*:\s*(\d+\.\d+)", result.stdout)
        duration = float(time_match.group(1)) if time_match else 0.0
        return duration
    except subprocess.CalledProcessError:
        return None

def main():
    p = 3
    n = p + 1
    e_values = [1, 5, 10, 15, 20, 25, 30, 35, 38]
    iterations = 10
    
    print(f"=== V2 Ring Lifting (Precomputed Seed): vary e, fixed p={p} ===")
    
    results = {}
    
    with open(os.path.join(RESULTS_DIR, "log_runner_ring_vary_e_v2.txt"), "w") as log:
        log.write(f"=== V2 Ring Lifting (Precomputed): vary e, fixed p={p} ===\n")
        log.write(f"e_values: {e_values}\n")
        log.write(f"Iterations: {iterations} (trimmed mean of 8)\n\n")
        
        for e in e_values:
            print(f"p={p}, e={e}:")
            log.write(f"e={e}:\n")
            
            times = []
            for i in range(iterations):
                t = run_v2(p, e, n)
                if t is not None:
                    times.append(t)
                    print(f"  iter {i+1}: {t:.6f}s")
                    log.write(f"  iter {i+1}: {t:.6f}s\n")
                else:
                    print(f"  iter {i+1}: FAILED")
                    log.write(f"  iter {i+1}: FAILED\n")
            
            if len(times) >= 3:
                sorted_times = sorted(times)
                trimmed = sorted_times[1:-1]
                mean_t = sum(trimmed) / len(trimmed)
            elif len(times) > 0:
                mean_t = sum(times) / len(times)
            else:
                mean_t = 0.0
                
            results[str(e)] = mean_t
            
            summary = f"  >> mean = {mean_t:.8f}s"
            print(summary + "\n")
            log.write(summary + "\n\n")
            log.flush()
            
    with open(os.path.join(RESULTS_DIR, "ring_vary_e_v2.json"), "w") as f:
        json.dump(results, f, indent=4)
        
    print("[Done] Saved to ring_vary_e_v2.json")

if __name__ == "__main__":
    if not os.path.exists(DICKSON_BENCH):
        print(f"Error: {DICKSON_BENCH} not found. Please compile.")
    else:
        main()
