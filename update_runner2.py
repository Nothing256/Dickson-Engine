import sys

with open("benchmark/runner_exp2_ring_medium.py", "r") as f:
    content = f.read()

content = content.replace("dickson_v2_find_primitive_seed(P, M, N)", "dickson_v2_find_primitive_seed(P, N)")
content = content.replace("dickson_v2_full_pipeline(p, e, m, seed, n)", "dickson_v2_full_pipeline(p, e, seed, n)")
content = content.replace("run_v2(P, e, M, v2_seed, N)", "run_v2(P, e, v2_seed, N)")
content = content.replace("def run_v2(p, e, m, seed, n):", "def run_v2(p, e, seed, n):")

with open("benchmark/runner_exp2_ring_medium.py", "w") as f:
    f.write(content)
