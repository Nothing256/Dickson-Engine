import subprocess
import os
import re

# --- Configuration ---
DICKSON_BIN = "build/bin/dickson_bench"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_v2(p, e, n):
    cmd = [DICKSON_BIN, str(p), str(e), str(n), "--random"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse Time Elapsed
        time_match = re.search(r"Time Elapsed\s*:\s*(\d+\.\d+)", result.stdout)
        duration = float(time_match.group(1)) if time_match else 0.0
        return duration
    except subprocess.CalledProcessError as e:
        print(f"Error running V2 for p={p}, e={e}:")
        return None

def main():
    print("\n=========================================================")
    print("=== Ring Factorization Benchmark: Dickson Engine V2 ===")
    print("=========================================================")
    print("Model: n = p+1, Jacobian-free Remainder Extraction + Universal Array Dispatch")
    
    # User requested a large muscular prime
    p = 30011
    n = p + 1
    print(f"Testing Constant Prime p={p} (n={n})")
    
    e_values = [1, 10, 50, 100, 200, 300, 400, 500, 750, 1000]
    
    print(f"Testing precisions (e): {e_values}")
    
    with open("log_v2_ring.txt", "w") as log:
        log.write(f"=== V2 Ring Tracking Benchmark (p={p}) ===\n")
        
        for e in e_values:
            print(f"  Testing V2 at e={e}... ", end="", flush=True)
            t = run_v2(p, e, n)
            if t is not None:
                record = f"e={e:<4} | Time: {t:.8f}s"
                print(f"Time={t:.6f}s")
                log.write(record + "\n")
            else:
                print("FAILED")
                log.write(f"e={e:<4} | FAILED\n")
                break
                
    print(f"V2 Benchmark complete. Log saved to log_v2_ring.txt")

if __name__ == "__main__":
    if not os.path.exists(DICKSON_BIN):
        print("Please compile first: make")
    else:
        main()
