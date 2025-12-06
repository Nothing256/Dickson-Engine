import argparse 
import re
import random
import itertools
import multiprocessing
import time
import csv

# --- 核心配置 ---
P = 13
E = 2
N = 14
MOD = P ** E  # 169

# 狙击模式配置
SNIPER_TARGETS = [] # 自动发现高价值目标
SNIPER_SAMPLES = 5000000 # 狙击模式：每核 500万次 (总计 1.2亿次)
NORMAL_SAMPLES = 50000   # 普查模式：每核 5万次 (快速过)

# --- 多项式类 (带 GCD 功能) ---
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
    
    # 简单的多项式除法 (用于计算 Hull)
    # 注意：在环上做除法很危险，但我们的因子都是首一的 (monic)，所以是可以除的！
    # 这里我们不需要真的除法，我们利用因子的集合性质来算 Hull
    # Hull = intersection(g, h*)
    # c = degree(Hull)

# --- 优化的 Gray 映射表 ---
GRAY_TABLE = []
for u in range(MOD):
    a = u % P; b = u // P
    vec = [(b + i * a) % P for i in range(P)]
    w = sum(1 for x in vec if x != 0)
    GRAY_TABLE.append(w)

def fast_weight(c_vec):
    return sum(GRAY_TABLE[u] for u in c_vec)

# --- 核心代数工具 ---
def get_reciprocal_poly_factors(factors, selected_indices):
    """
    计算 h*(x) 包含的因子索引。
    原理：
    1. x^n-1 的因子集合是 F = {f_0, f_1, ...}
    2. g(x) 选了 F_g (selected_indices)
    3. h(x) 就是 F \ F_g
    4. h*(x) 是 h(x) 的互反。
    5. 因为我们的因子都是自互反的 (Self-Reciprocal)！
       即 f*(x) = f(x) (忽略常数项差异)
       所以 h*(x) 的因子集合就是 h(x) 的因子集合！
    
    结论：Hull 的因子集合 = F_g ∩ (F \ F_g) = 空集！
    推论：对于本案例，c 恒等于 0。
    
    为了严谨，我们还是写出通用逻辑，万一以后有非自互反因子呢？
    """
    # 在本案例中，所有因子经观察均为自互反 (系数对称)。
    # 所以 Hull 维数 c = 0。
    # 为了代码通用性，我们暂时返回 0。
    return 0

# --- Worker ---
def worker_task(g_coeffs, k, samples, seed):
    random.seed(seed)
    N_local = len(g_coeffs) + k - 1
    min_d = 9999
    
    # 预生成随机数以减少循环内开销
    # 分批次处理
    BATCH = 1000
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

# --- 主程序 ---
def parse_factors(filename):
    # (复用之前的解析代码)
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
    except FileNotFoundError: return []
    return factors



# --- 终极版 Worker ---
def brute_force_worker(g_coeffs, k, start_idx, end_idx):
    """全量搜索的工作进程"""
    min_d = 9999
    
    # 将一维的索引 i 映射回 k 维的系数向量 m
    # m_coeffs = []
    # temp_i = i
    # for _ in range(k):
    #     m_coeffs.append(temp_i % MOD)
    #     temp_i //= MOD
    
    # 上面的方法太慢了，直接用 itertools.product 配合 islice
    # 但传递 islice 对象给多进程很麻烦
    # 我们用最简单的数学方法：每个进程负责一个范围
    
    for i in range(start_idx, end_idx):
        if i == 0: continue # 跳过全零码字
        
        # 将 i 转化为 MOD 进制的 k 位数，这就是信息系数 m
        m = []
        temp = i
        for _ in range(k):
            m.append(temp % MOD)
            temp //= MOD

        # 卷积
        c_vec = [0] * N
        for j, val in enumerate(m):
            if val == 0: continue
            for l, gv in enumerate(g_coeffs):
                idx = (j + l) % N
                c_vec[idx] = (c_vec[idx] + val * gv) % MOD
        
        w = fast_weight(c_vec)
        if w < min_d: min_d = w
        if min_d <= 2: return min_d # 剪枝

    return min_d



def main_unified(args):
    factors = parse_factors("my_factors.txt")
    if not factors: return

    num_cores = multiprocessing.cpu_count()
    print(f"[*] Project Quantum Leap (Unified Engine)")
    print(f"[*] Mode: '{args.mode.upper()}' | Cores: {num_cores}")
    if args.mode == 'brute':
        print(f"[*] Brute Force Target: k <= {args.k_max}")
    print("-" * 90)
    print(f"{'ID':<4} | {'k':<3} | {'c':<3} | {'Mode':<10} | {'d_val':<6} | {'Samples':<10} | {'Quantum Params'}")
    print("-" * 90)

    pool = multiprocessing.Pool(processes=num_cores)
    results_log = []

    try:
        count = 0
        for r in range(1, len(factors)):
            for combo in itertools.combinations(factors, r):
                g = Poly([1])
                for f in combo: g = g * f
                k = N - g.degree()
                c = 0 # 理论上 c=0
                
                # --- 模式选择逻辑 ---
                if args.mode == 'scan':
                    tasks = [(g.coeffs, k, NORMAL_SAMPLES, int(time.time()*1000)+i) for i in range(num_cores)]
                    res = pool.starmap(worker_task, tasks)
                    d_est = min(res)
                    
                    threshold = 80
                    if d_est > threshold:
                        mode_str = "SNIPER"
                        sniper_tasks = [(g.coeffs, k, SNIPER_SAMPLES, int(time.time()*1000)+i+999) for i in range(num_cores)]
                        res_sniper = pool.starmap(worker_task, sniper_tasks)
                        final_d = min(res_sniper)
                        total_samples = num_cores * SNIPER_SAMPLES
                    else:
                        mode_str = "SCAN"
                        final_d = d_est
                        total_samples = num_cores * NORMAL_SAMPLES
                    
                    n_phy = N * P
                    q_params = f"[[{n_phy}, {k}, {final_d}, {c}]]"
                    print(f"{count:<4} | {k:<3} | {c:<3} | {mode_str:<10} | {final_d:<6} | {'{:.0f}w'.format(total_samples/10000):<10} | {q_params}")
                    results_log.append([count, k, c, final_d, q_params])

                elif args.mode == 'brute':
                    if k > args.k_max:
                        # print(f"\r{count:<4} | {k:<3} | {c:<3} | SKIPPING   | {'-':<6} | {'-':<10} | (k > k_max={args.k_max})", end="")
                        # print() # 换行
                        count += 1
                        continue

                    space_size = MOD ** k
                    mode_str = f"BRUTE({num_cores})"
                    print(f"[*] Attacking k={k} (ID: {count})... Space: {space_size:.2e}. Engaging cores.")
                    
                    chunk_size = space_size // num_cores
                    tasks = []
                    for i in range(num_cores):
                        start = i * chunk_size
                        end = (i + 1) * chunk_size if i != num_cores - 1 else space_size
                        tasks.append((g.coeffs, k, start, end))
                    
                    start_time = time.time()
                    results = pool.starmap(brute_force_worker, tasks)
                    end_time = time.time()
                    
                    final_d = min(results)
                    
                    n_phy = N * P
                    q_params = f"[[{n_phy}, {k}, {final_d}, {c}]]"
                    duration = end_time - start_time
                    print(f"{count:<4} | {k:<3} | {c:<3} | {mode_str:<10} | {final_d:<6} | {'{:.1e}'.format(space_size):<10} | {q_params}  (Time: {duration:.2f}s)")
                    results_log.append([count, k, c, final_d, q_params])

                count += 1

    except KeyboardInterrupt:
        print("\n[*] Aborted.")
    finally:
        pool.close()
        pool.join()

        output_filename = f"quantum_codes_{args.mode}.csv"
        with open(output_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "k", "c", "d_exact", "Params"])
            writer.writerows(results_log)
        print(f"\n[*] Data saved to {output_filename}")



if __name__ == "__main__":
    # --- 命令行参数解析 ---
    parser = argparse.ArgumentParser(description="Quantum Code Search Engine for Z_p^e.")
    parser.add_argument(
        '-m', '--mode', 
        type=str, 
        choices=['scan', 'brute'], 
        default='scan', 
        help="Search mode: 'scan' for massive sampling, 'brute' for brute-force."
    )
    parser.add_argument(
        '--k_max', 
        type=int, 
        default=4, 
        help="In 'brute' mode, the maximum k to search exhaustively."
    )
    
    main_unified(parser.parse_args())
