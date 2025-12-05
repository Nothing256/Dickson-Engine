import subprocess
import os
import re
import sys

# --- 1. 简单的素数生成器 ---
def generate_primes(n):
    """生成 n 以内的所有素数"""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]

def parse_factors(output_text):
    """
    解析因子列表，提取 x^2 + Ax + 1 中的 A。
    兼容两种格式：
    1. Dickson (代数式): [idx] (x^2 + 4x + 1)
    2. NTL (向量式):     [1 4 1]
    """
    coeffs = []
    for line in output_text.splitlines():
        line = line.strip()
        
        # --- 策略 A: 解析 NTL 向量格式 [c0 c1 c2] ---
        if line.startswith("[") and line.endswith("]"):
            content = line.strip("[]")
            parts = content.split()
            
            if len(parts) == 3:
                try:
                    val = int(parts[1])
                    
                    # [关键修正] 如果中间系数是 0，说明是 x^2 + 1
                    # Dickson 解析逻辑里忽略了 x^2 + 1，所以这里也要忽略，保持对齐
                    if val == 0:
                        continue
                        
                    coeffs.append(val)
                except ValueError:
                    pass
            continue 

        # --- 策略 B: 解析 Dickson 代数格式 ---
        if "(x - 1)" in line or "(x + 1)" in line or "(x^2 + 1)" in line:
            continue
            
        match = re.search(r"x\^2\s*([+-])\s*(\d*)\*?[\s]*x\s*\+\s*1", line)
        
        if match:
            sign = match.group(1)
            raw_val = match.group(2)
            
            if raw_val:
                val = int(raw_val)
            else:
                val = 1 
            
            if sign == '-':
                val = -val
            
            coeffs.append(val)
            
    return sorted(coeffs)

# --- 3. 运行器 ---
def run_verification():
    # 配置
    PRIME_LIMIT = 2000  # 测试范围
    TARGET_E = 3        # 统一提升到 p^3
    
    # 路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DICKSON_BIN = os.path.join(BASE_DIR, "build", "bin", "dickson_cli")
    NTL_BIN = os.path.join(BASE_DIR, "build", "bin", "ntl_bench")
    
    if not os.path.exists(DICKSON_BIN) or not os.path.exists(NTL_BIN):
        print("Error: Binaries not found. Check build/bin/")
        return

    print(f"=== Starting Cross-Validation (p < {PRIME_LIMIT}, e = {TARGET_E}) ===")
    
    primes = generate_primes(PRIME_LIMIT)
    # 【关键修正】过滤掉 p <= 3，因为 p=3 会导致随机种子搜索除以零
    primes = [p for p in primes if p > 3]
    
    pass_count = 0
    fail_count = 0
    
    for p in primes:
        print(f"Testing p={p}...", end="", flush=True)
        
        # --- 1. 运行 Dickson ---
        dickson_file = "temp_dickson.txt"
        cmd_dickson = [DICKSON_BIN, str(p), str(TARGET_E), "--auto", "--output", dickson_file]
        
        # 捕获错误，而不是直接吞掉
        proc_d = subprocess.run(cmd_dickson, capture_output=True, text=True)
        
        if proc_d.returncode != 0:
            print(" CRASHED (Dickson CLI) ❌")
            print(f"STDERR: {proc_d.stderr}")
            fail_count += 1
            continue

        if not os.path.exists(dickson_file):
            print(" FAILED (No Output File) ❌")
            fail_count += 1
            continue

        with open(dickson_file, "r") as f:
            dickson_out = f.read()
            
        # --- 2. 运行 NTL ---
        # 你的需求：保存 NTL 结果
        ntl_file = "temp_ntl.txt"
        cmd_ntl = [NTL_BIN, str(p), "1"] # NTL run at e=1
        proc_ntl = subprocess.run(cmd_ntl, capture_output=True, text=True)
        
        # 保存 NTL 输出到文件
        with open(ntl_file, "w") as f:
            f.write(proc_ntl.stdout)
            
        ntl_out = proc_ntl.stdout
        
        # --- 3. 解析与对比 ---
        coeffs_dickson = parse_factors(dickson_out)
        coeffs_ntl = parse_factors(ntl_out)
        
        # 验证逻辑：Dickson (mod p^e) % p == NTL (mod p)
        coeffs_dickson_mod_p = sorted([c % p for c in coeffs_dickson])
        
        set_dickson = set(coeffs_dickson_mod_p)
        set_ntl = set(coeffs_ntl)
        
        if set_dickson == set_ntl:
            print(" PASS ✅")
            pass_count += 1
        else:
            print(" FAIL ❌")
            print(f"  Dickson (mod p): {set_dickson}")
            print(f"  NTL:             {set_ntl}")
            fail_count += 1
            # 失败时保留临时文件以便检查
            break 
            
    # 清理临时文件 (如果成功才清理，失败保留现场)
    if fail_count == 0:
        if os.path.exists("temp_dickson.txt"): os.remove("temp_dickson.txt")
        if os.path.exists("temp_ntl.txt"): os.remove("temp_ntl.txt")
        
    print("========================================")
    print(f"Summary: {pass_count} Passed, {fail_count} Failed.")
    
if __name__ == "__main__":
    run_verification()
