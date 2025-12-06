import argparse 
import re
import random
import itertools
import multiprocessing
import time
import csv
import os

# --- 核心配置 ---
P = 13
E = 2
N = 14
MOD = P ** E  # 169

# 采样策略配置
NORMAL_SAMPLES = 50000   # 普查模式：每核 5万次
SNIPER_SAMPLES = 5000000 # 狙击模式：每核 500万次
SNIPER_THRESHOLD = 80    # 触发狙击的 d 阈值

# --- 多项式类 ---
class Poly:
    def __init__(self, coeffs):
        self.coeffs = [c % MOD for c in coeffs]
        self.trim()
    def trim(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0: self.coeffs.pop()
    def degree(self): return len(self.coeffs) - 1
    def __mul__(self, other):
        res = [0] * (self.degree() + other.degree() + 1)
        for i, c1 in enumerate(self.coeffs):
            for j, c2 in enumerate(other.coeffs):
                res[i+j] = (res[i+j] + c1 * c2) % MOD
        return Poly(res)
    def __repr__(self): return str(self.coeffs)

# --- 优化的 Gray 映射表 ---
GRAY_TABLE = []
for u in range(MOD):
    a = u % P; b = u // P
    vec = [(b + i * a) % P for i in range(P)]
    w = sum(1 for x in vec if x != 0)
    GRAY_TABLE.append(w)

def fast_weight(c_vec):
    return sum(GRAY_TABLE[u] for u in c_vec)

# --- 核心代数工具: 因子解析 ---
def parse_factors(filename):
    factors = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                match = re.search(r'\((.*?)\)', line)
                if not match: continue
                poly_str = match.group(1).replace(" ", "")
                coeffs = []
                if "x^2" in poly_str:
                    match_mid = re.search(r'x\^2\+(\d+)x\+1', poly_str)
                    if match_mid: coeffs = [1, int(match_mid.group(1)), 1]
                    elif poly_str == "x^2+1": coeffs = [1, 0, 1]
                    elif "x^2+x+1" in poly_str: coeffs = [1, 1, 1]
                elif "x-1" in poly_str: coeffs = [-1, 1]
                elif "x+1" in poly_str: coeffs = [1, 1]
                if coeffs: factors.append(Poly(coeffs))
    except FileNotFoundError: 
        print(f"[!] Error: {filename} not found.")
        return []
    return factors

# --- 任务 Worker: 采样模式 ---
def worker_sample_task(g_coeffs, k, samples, seed):
    random.seed(seed)
    N_local = len(g_coeffs) + k - 1
    min_d = 9999
    
    # 分批次处理以减少开销
    BATCH = 2000
    for _ in range(0, samples, BATCH):
        curr_batch = min(BATCH, samples - _)
        for __ in range(curr_batch):
            m = [random.randint(0, MOD-1) for _ in range(k)]
            if all(c == 0 for c in m): continue
            
            c_vec = [0] * N_local
            for i, val in enumerate(m):
                if val == 0: continue
                for j, gv in enumerate(g_coeffs):
                    idx = (i + j) % N_local
                    c_vec[idx] = (c_vec[idx] + val * gv) % MOD
            
            w = fast_weight(c_vec)
            if w < min_d: min_d = w
            if min_d <= 2: return min_d
    return min_d

# --- 任务 Worker: 全量模式 ---
def worker_brute_task(g_coeffs, k, start_idx, end_idx):
    min_d = 9999
    N_local = len(g_coeffs) + k - 1
    
    for i in range(start_idx, end_idx):
        if i == 0: continue 
        # 将索引转回系数向量
        m = []
        temp = i
        for _ in range(k):
            m.append(temp % MOD)
            temp //= MOD

        c_vec = [0] * N_local
        for j, val in enumerate(m):
            if val == 0: continue
            for l, gv in enumerate(g_coeffs):
                idx = (j + l) % N_local
                c_vec[idx] = (c_vec[idx] + val * gv) % MOD
        
        w = fast_weight(c_vec)
        if w < min_d: min_d = w
        if min_d <= 2: return min_d 

    return min_d

# --- 主程序逻辑 ---
def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Phoenix Project: Quantum Code Search Engine (Final Edition).")
    parser.add_argument('-m', '--mode', type=str, choices=['scan', 'brute'], default='scan', 
                        help="Search mode: 'scan' (sampling) or 'brute' (exhaustive).")
    parser.add_argument('--k_max', type=int, default=4, 
                        help="In 'brute' mode, max dimension k to search exhaustively.")
    args = parser.parse_args()

    # 加载因子
    factors_raw = parse_factors("my_factors.txt")
    if not factors_raw: return
    
    # 给因子编号 (Index, Poly)
    factors_with_indices = list(enumerate(factors_raw))

    num_cores = multiprocessing.cpu_count()
    print(f"[*] Project Phoenix: Quantum Search Engine")
    print(f"[*] Mode: {args.mode.upper()} | Cores: {num_cores}")
    if args.mode == 'brute':
        print(f"[*] Target: Brute Force for k <= {args.k_max}")
    
    print("-" * 115)
    print(f"{'ID':<4} | {'k':<3} | {'c':<3} | {'Mode':<10} | {'d_best':<6} | {'Samples/Space':<15} | {'Factor Indices':<20} | {'Params'}")
    print("-" * 115)

    pool = multiprocessing.Pool(processes=num_cores)
    results_log = []

    try:
        count = 0
        # 遍历组合长度 r
        for r in range(1, len(factors_with_indices)):
            # 遍历具体的组合 (同时也获取索引)
            for combo_with_indices in itertools.combinations(factors_with_indices, r):
                
                indices, combo_polys = zip(*combo_with_indices)
                factor_indices_str = str(indices)

                # 构造生成多项式
                g = Poly([1])
                for f in combo_polys: g = g * f
                k = N - g.degree()
                c = 0 # 理论上 c=0 (LCD)

                mode_str = ""
                final_d = 0
                sample_info = ""

                # --- 模式 A: 扫描 (Scan) ---
                if args.mode == 'scan':
                    # 1. 普查
                    tasks = [(g.coeffs, k, NORMAL_SAMPLES, int(time.time()*1000)+i) for i in range(num_cores)]
                    res = pool.starmap(worker_sample_task, tasks)
                    d_est = min(res)
                    
                    # 2. 狙击判断
                    if d_est > SNIPER_THRESHOLD:
                        mode_str = "SNIPER"
                        sniper_tasks = [(g.coeffs, k, SNIPER_SAMPLES, int(time.time()*1000)+i+999) for i in range(num_cores)]
                        res_sniper = pool.starmap(worker_sample_task, sniper_tasks)
                        final_d = min(res_sniper)
                        total = num_cores * SNIPER_SAMPLES
                    else:
                        mode_str = "SCAN"
                        final_d = d_est
                        total = num_cores * NORMAL_SAMPLES
                    
                    sample_info = f"{total/10000:.0f}w (S)"

                # --- 模式 B: 强攻 (Brute) ---
                elif args.mode == 'brute':
                    if k > args.k_max:
                        # 跳过不打印，或者打印简略信息
                        # print(f"\rSkipping k={k}...", end="")
                        count += 1
                        continue
                    
                    space_size = MOD ** k
                    mode_str = f"BRUTE({num_cores})"
                    
                    # 任务切分
                    chunk_size = space_size // num_cores
                    tasks = []
                    for i in range(num_cores):
                        start = i * chunk_size
                        end = (i + 1) * chunk_size if i != num_cores - 1 else space_size
                        tasks.append((g.coeffs, k, start, end))
                    
                    start_time = time.time()
                    results = pool.starmap(worker_brute_task, tasks)
                    end_time = time.time()
                    
                    final_d = min(results)
                    sample_info = f"{space_size:.1e} (All)"

                # --- 输出与记录 ---
                n_phy = N * P
                q_params = f"[[{n_phy}, {k}, {final_d}, {c}]]"
                
                print(f"{count:<4} | {k:<3} | {c:<3} | {mode_str:<10} | {final_d:<6} | {sample_info:<15} | {factor_indices_str:<20} | {q_params}")
                
                # 统一的 CSV 格式
                results_log.append([count, k, c, final_d, factor_indices_str, q_params])
                count += 1

    except KeyboardInterrupt:
        print("\n[*] Operation Aborted by User.")
    finally:
        pool.close()
        pool.join()

        # 保存结果
        output_filename = f"quantum_codes_{args.mode}.csv"
        with open(output_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "k", "c", "d_best", "Factor Indices", "Params"])
            writer.writerows(results_log)
        print(f"\n[*] Results saved to {output_filename}")

if __name__ == "__main__":
    main()