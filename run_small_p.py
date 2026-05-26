import subprocess
import time

def run_v1(p, e):
    cmd = ["build/bin/dickson_cli", str(p), str(e), "--silent", "--full", "2"]
    start = time.time()
    subprocess.run(cmd, capture_output=True, text=True)
    return time.time() - start

def run_v2(p, e):
    n = p + 1
    cmd = ["build/bin/dickson_bench", str(p), str(e), str(n), "--random"]
    start = time.time()
    subprocess.run(cmd, capture_output=True, text=True)
    return time.time() - start

for e in [1, 10, 20, 30, 38]:
    t1 = run_v1(3, e)
    t2 = run_v2(3, e)
    print(f"e={e} | V1: {t1:.6f}s | V2: {t2:.6f}s")
