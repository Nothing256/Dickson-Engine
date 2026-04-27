import subprocess
import os
import re
import matplotlib.pyplot as plt

# --- Configurations ---
NTL_BIN_V2 = "build/bin/ntl_bench_v2"
DICKSON_BIN_V2 = "build/bin/dickson_bench_v2"
RESULTS_DIR = "benchmark/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_bench(executable, p, e=1, n=None, extra_args=None):
    """Run benchmark and return elapsed time."""
    cmd = [executable, str(p), str(e)]
    if n is not None:
        cmd.append(str(n))
    if extra_args:
        cmd.extend(extra_args)
        
    try:
        # Redirect output to parse execution time
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        time_match = re.search(r"Time Elapsed\s*:\s*(\d+\.\d+)", result.stdout)
        duration = float(time_match.group(1)) if time_match else 0.0
        return duration
    except subprocess.CalledProcessError as e:
        print(f"Error running {executable} {' '.join(extra_args or [])} for p={p}:")
        return None

def run_triple_comparison():
    print("\n=========================================================")
    print("=== Triple Benchmark: NTL Vs Dickson (Auto-Seed) Vs Dickson (Precomputed) ===")
    print("=========================================================")
    
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 47, 53, 59, 61, 67, 71, 79, 83, 89, 97, 101, 107, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
    
    times_ntl = []
    times_dickson_auto = []
    times_dickson_precomputed = []
    
    valid_primes_ntl = []
    valid_primes_dickson = []
    
    # Pre-check if Precomputed Table supports max prime inside the engine
    # (assuming dictionary covers up to some N. If precomputed fails, python handles the 'None' gracefully)
    
    print("Running n=p^2+p+1 complexity benchmarks...")

    for p in primes:
        n_dimension = p**2 + p + 1
        print(f"  Testing p={p} (n={n_dimension})... ", end="", flush=True)
        
        # 1. NTL (Cap elevated to 200 to capture the 60+ second explosion)
        if p <= 200: 
            t_n = run_bench(NTL_BIN_V2, p, e=1)
            time_n_str = f"{t_n:.4f}s" if t_n is not None else "CRASH"
            if t_n is not None:
                times_ntl.append(t_n)
                valid_primes_ntl.append(p)
        else:
            time_n_str = "SKI (O(p^4))"

        # 2. Dickson V2 (Auto-Seeder)
        t_d_auto = run_bench(DICKSON_BIN_V2, p, e=1, extra_args=["--random"])
        time_d_auto_str = f"{t_d_auto:.6f}s" if t_d_auto is not None else "CRASH"
        
        # 3. Dickson V2 (Precomputed Oxygen Tank)
        t_d_pre = run_bench(DICKSON_BIN_V2, p, e=1)
        time_d_pre_str = f"{t_d_pre:.6f}s" if t_d_pre is not None else "CRASH/MISSING_SEED"
        
        if t_d_auto is not None and t_d_pre is not None:
            times_dickson_auto.append(t_d_auto)
            times_dickson_precomputed.append(t_d_pre)
            valid_primes_dickson.append(p)
            
        print(f"NTL: {time_n_str} | Dick(Auto): {time_d_auto_str} | Dick(Pre): {time_d_pre_str}")

    # Plotting
    plt.figure(figsize=(12, 7))
    plt.plot(valid_primes_ntl, times_ntl, 'r-o', linewidth=2, markersize=8, label='NTL (CanZass) O(p^4)')
    plt.plot(valid_primes_dickson, times_dickson_auto, 'b--s', linewidth=2, markersize=8, label='Dickson V2 (Auto-Seeder)')
    plt.plot(valid_primes_dickson, times_dickson_precomputed, 'g-^', linewidth=2, markersize=8, label='Dickson V2 (Precomputed Seed)')
    
    plt.title('Triple Benchmark: NTL vs. Dickson Generative Paradigms', fontsize=14)
    plt.xlabel('Prime Characteristic (p)', fontsize=12)
    plt.ylabel('Time Elapsed (seconds)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    plt.yscale('log') 
    
    save_path = os.path.join(RESULTS_DIR, "v2_triple_comparison.png")
    plt.savefig(save_path)
    print(f"\n[Success] Triple Comparison Graph saved to '{save_path}'")

if __name__ == "__main__":
    if not os.path.exists(NTL_BIN_V2) or not os.path.exists(DICKSON_BIN_V2):
        print("Error: Binaries not found. Please compile them first via 'make' in build/.")
    else:
        run_triple_comparison()
