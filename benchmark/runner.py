import subprocess
import os
import re
import matplotlib.pyplot as plt
import time

# --- 配置 ---
DICKSON_BIN = "build/bin/dickson_cli"
NTL_BIN = "build/bin/ntl_bench"
RESULTS_DIR = "benchmark/results"

# 确保结果目录存在
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- 辅助函数 ---
def run_command(cmd):
    """运行命令并解析 Time Elapsed"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # 正则提取时间: "Time Elapsed       : 0.001234 s"
        match = re.search(r"Time Elapsed\s*:\s*(\d+\.\d+)", result.stdout)
        if match:
            return float(match.group(1))
        return 0.0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(e.stderr)
        return None

def generate_primes_range(start, end, count):
    """生成指定范围内的 count 个素数（均匀分布）"""
    primes = []
    # 简单的筛选
    sieve = [True] * (end + 1)
    for i in range(2, int(end**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, end + 1, i):
                sieve[j] = False
    all_primes = [i for i in range(start, end) if sieve[i]]
    
    # 均匀采样
    if len(all_primes) <= count:
        return all_primes
    step = len(all_primes) // count
    return all_primes[::step][:count]

# --- 实验 1: Time vs Prime (Complexity) ---
def run_experiment_1():
    print("\n=== Experiment 1: Time vs Prime (p) ===")
    print("Goal: Compare Complexity O(p) vs O(p^2)")
    
    # 设置：e=1 (在基域上比，这是 NTL 的主场，但我们要在这里击败它)
    FIXED_E = 1
    
    # 选取素数样本: 100 到 5000 之间的 20 个素数
    # 为了画图好看，我们可以选大一点，比如到 10000
    primes = generate_primes_range(100, 10000, 20)
    
    times_dickson = []
    times_ntl = []
    valid_primes = []

    print(f"Running on {len(primes)} primes: {primes}")

    for p in primes:
        print(f"  Testing p={p}...", end="", flush=True)
        
        # 1. Dickson (Auto mode)
        # 注意：包含寻找种子的时间
        t_d = run_command([DICKSON_BIN, str(p), str(FIXED_E), "--auto", "--silent"])
        
        # 2. NTL (Standard)
        t_n = run_command([NTL_BIN, str(p), str(FIXED_E)])
        
        if t_d is not None and t_n is not None:
            times_dickson.append(t_d)
            times_ntl.append(t_n)
            valid_primes.append(p)
            print(f" Dickson={t_d:.4f}s, NTL={t_n:.4f}s")
        else:
            print(" Failed.")

    # 画图
    plt.figure(figsize=(10, 6))
    plt.plot(valid_primes, times_ntl, 'r-o', label='NTL (CanZass)')
    plt.plot(valid_primes, times_dickson, 'b-^', label='Dickson-Engine (Ours)')
    
    plt.title(f'Factorization Performance: Time vs Prime Size (e={FIXED_E})')
    plt.xlabel('Prime Characteristic (p)')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.legend()
    
    save_path = os.path.join(RESULTS_DIR, "experiment_time_vs_p.png")
    plt.savefig(save_path)
    print(f"Graph saved to {save_path}")

# --- 实验 2: Time vs Precision (Lifting Cost) ---
def run_experiment_2():
    print("\n=== Experiment 2: Time vs Precision (e) ===")
    print("Goal: Demonstrate Linear Lifting Complexity O(e)")
    
    # 设置：固定一个中等大小的 p
    FIXED_P = 1009
    
    # e 从 1 到 100
    e_values = [1, 5, 10, 20, 30, 40, 50, 75, 100]
    
    times_dickson = []
    
    print(f"Fixed p={FIXED_P}. Scaling e: {e_values}")
    
    for e in e_values:
        print(f"  Testing e={e}...", end="", flush=True)
        
        # Dickson (Auto mode)
        t_d = run_command([DICKSON_BIN, str(FIXED_P), str(e), "--auto", "--silent"])
        
        if t_d is not None:
            times_dickson.append(t_d)
            print(f" Time={t_d:.4f}s")
        
        # 注意：这里不跑 NTL，因为 NTL 不支持 Ring Lifting (e>1)，会崩或者只能跑 e=1
        # 我们只展示我们自己的线性特性

    # 画图
    plt.figure(figsize=(10, 6))
    plt.plot(e_values, times_dickson, 'b-^', label='Dickson-Engine (Lifting)')
    
    plt.title(f'Lifting Performance: Time vs Precision e (p={FIXED_P})')
    plt.xlabel('Precision Exponent (e)')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.legend()
    
    save_path = os.path.join(RESULTS_DIR, "experiment_time_vs_e.png")
    plt.savefig(save_path)
    print(f"Graph saved to {save_path}")

if __name__ == "__main__":
    if not os.path.exists(DICKSON_BIN):
        print("Please build binaries first!")
    else:
        run_experiment_1()
        run_experiment_2()
