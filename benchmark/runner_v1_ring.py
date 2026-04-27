import subprocess
import os
import re

# --- Configuration ---
DICKSON_CLI_V1 = "build/bin/dickson_cli"
RESULTS_DIR = "benchmark/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_v1(p, e):
    cmd = [DICKSON_CLI_V1, str(p), str(e), "--auto", "--silent"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse Time Elapsed
        time_match = re.search(r"Time Elapsed\s*:\s*(\d+\.\d+)", result.stdout)
        duration = float(time_match.group(1)) if time_match else 0.0
        return duration
    except subprocess.CalledProcessError as e:
        print(f"Error running V1 for p={p}, e={e}:")
        return None

def main():
    print("\n=========================================================")
    print("=== Ring Factorization Benchmark: Dickson Engine V1 ===")
    print("=========================================================")
    print("Model: n = p+1, V(x) Seed Discovery + single-variable Newton Lifting")
    
    # User requested a large muscular prime
    p = 30011
    print(f"Testing Constant Prime p={p}")
    
    e_values = [1, 10, 50, 100, 200, 300, 400, 500, 750, 1000]
    
    print(f"Testing precisions (e): {e_values}")
    
    with open(os.path.join("benchmark", "log_v1_ring.txt"), "w") as log:
        log.write(f"=== V1 Ring Lifting Benchmark (p={p}) ===\n")
        
        for e in e_values:
            print(f"  Testing V1 at e={e}... ", end="", flush=True)
            t = run_v1(p, e)
            if t is not None:
                record = f"e={e:<4} | Time: {t:.8f}s"
                print(f"Time={t:.6f}s")
                log.write(record + "\n")
            else:
                print("FAILED")
                log.write(f"e={e:<4} | FAILED\n")
                break
                
    print(f"V1 Benchmark complete. Log saved to benchmark/log_v1_ring.txt")

if __name__ == "__main__":
    if not os.path.exists(DICKSON_CLI_V1):
        print("Please compile first: make")
    else:
        main()
