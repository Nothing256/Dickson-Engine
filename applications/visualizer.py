import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

# --- 核心配置 ---
P = 13
E = 2
N = 14
N_PHY = N * P  # 182
Q = 13         

def griesmer_bound_n_min(k, d, q):
    """Griesmer Bound: Given k, d, q, return min n required."""
    val = 0
    for i in range(k):
        val += math.ceil(d / (q ** i))
    return val

def calculate_theoretical_max_d(n_phy, k, q):
    """Given n, k, q, return max possible d according to Griesmer."""
    # 从 n_phy 开始向下尝试 d
    for d in range(n_phy, 0, -1):
        n_needed = griesmer_bound_n_min(k, d, q)
        if n_needed <= n_phy:
            return d
    return 1

def main():
    print("[*] Project Skyline: Final Visualization (Classical LCD Mode)")
    
    # 1. 读取数据
    # 尝试读取我们生成的各种 CSV
    dfs = []
    try:
        dfs.append(pd.read_csv("quantum_codes_final.csv").assign(source='Scan'))
    except: pass
    
    try:
        # 尝试读取强攻版数据 (可能是 brute.csv 或 brute_force.csv)
        dfs.append(pd.read_csv("quantum_codes_brute.csv").assign(source='Brute'))
    except: 
        try:
            dfs.append(pd.read_csv("quantum_codes_brute_force.csv").assign(source='Brute'))
        except: pass

    if not dfs:
        print("[!] No data files found!")
        return

    df_all = pd.concat(dfs, ignore_index=True)

    # 2. 数据融合 (清洗与去重)
    # 逻辑：对于每个 k，我们要找 d 最大的。
    # 如果 d 一样，优先选 source='Brute' 的。
    
    best_codes = {} # k -> {'d': val, 'source': type}

    for _, row in df_all.iterrows():
        k = int(row['k'])
        # 兼容列名 d_best / d_exact / d_val
        if 'd_exact' in row and not pd.isna(row['d_exact']): d = int(row['d_exact'])
        elif 'd_best' in row and not pd.isna(row['d_best']): d = int(row['d_best'])
        elif 'd_val' in row and not pd.isna(row['d_val']): d = int(row['d_val'])
        else: continue

        src = row['source']

        # 初始化
        if k not in best_codes:
            best_codes[k] = {'d': d, 'source': src}
            continue
        
        # 更新逻辑
        current_d = best_codes[k]['d']
        current_src = best_codes[k]['source']

        if d > current_d:
            # 发现更好的 d，直接更新
            best_codes[k] = {'d': d, 'source': src}
        elif d == current_d and src == 'Brute':
            # d 一样，但我是 Brute，我的置信度更高，覆盖它！
            best_codes[k] = {'d': d, 'source': src}

    # 准备绘图数据
    k_list = sorted(best_codes.keys())
    d_list = [best_codes[k]['d'] for k in k_list]
    sources = [best_codes[k]['source'] for k in k_list]

    # 3. 计算理论极限 (Griesmer)
    griesmer_d = []
    for k in k_list:
        griesmer_d.append(calculate_theoretical_max_d(N_PHY, k, Q))

    # 4. 打印最终表格 (Latex 风格)
    print("\n" + "="*70)
    print(f"{'k':<5} | {'d_opt':<10} | {'d_griesmer':<12} | {'Gap':<5} | {'Type'}")
    print("-" * 70)
    for i, k in enumerate(k_list):
        gap = griesmer_d[i] - d_list[i]
        src_mark = "Exact" if sources[i] == 'Brute' else "Est."
        print(f"{k:<5} | {d_list[i]:<10} | {griesmer_d[i]:<12} | {gap:<5} | {src_mark}")
    print("="*70)

    # 5. 绘图
    plt.figure(figsize=(10, 6), dpi=300)
    
    # 理论线
    plt.plot(k_list, griesmer_d, 'r--', linewidth=2, alpha=0.7, label='Theoretical Bound (Griesmer)')
    
    # 我们的曲线
    plt.plot(k_list, d_list, color='teal', linewidth=2, alpha=0.4, zorder=1)

    # 区分绘制点
    k_exact = [k for i, k in enumerate(k_list) if sources[i] == 'Brute']
    d_exact = [d_list[i] for i, k in enumerate(k_list) if sources[i] == 'Brute']
    
    k_est = [k for i, k in enumerate(k_list) if sources[i] == 'Scan']
    d_est = [d_list[i] for i, k in enumerate(k_list) if sources[i] == 'Scan']

    # 绘制
    if k_est:
        plt.scatter(k_est, d_est, color='blue', s=80, marker='o', label='This Work (Probabilistic)', zorder=2)
    
    if k_exact:
        plt.scatter(k_exact, d_exact, color='gold', s=200, marker='*', edgecolors='black', linewidth=0.5, label='This Work (Exact/Brute)', zorder=3)

    # 标注数值
    for i, k in enumerate(k_list):
        offset = 5 if k % 2 == 0 else -10 # 错开标注防止重叠
        plt.text(k, d_list[i] + offset, f"{d_list[i]}", ha='center', fontsize=9, fontweight='bold')

    # 标题与标签 (学术化)
    plt.title(f'Optimal Classical LCD Codes over $\mathbb{{Z}}_{{169}}$ via Gray Map\n(Length $n={N_PHY}$, Alphabet size $q={Q}$)', fontsize=14)
    plt.xlabel('Dimension $k$', fontsize=12)
    plt.ylabel('Minimum Hamming Distance $d$', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("lcd_codes_performance.png")
    print(f"\n[*] Figure saved to 'lcd_codes_performance.png'")

if __name__ == "__main__":
    main()