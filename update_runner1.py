import sys

with open("benchmark/runner_exp1_domain_vary_p.py", "r") as f:
    content = f.read()

# Remove m from bench_v2_precomputed
content = content.replace("def bench_v2_precomputed(p, e, m, n, iteration):", "def bench_v2_precomputed(p, e, m, n, iteration):")
content = content.replace("dickson_v2_full_pipeline(p, e, m, seed, n)", "dickson_v2_full_pipeline(p, e, seed, n)")

# Remove m from bench_v2_auto
content = content.replace("def bench_v2_auto(p, e, m, n, iteration):", "def bench_v2_auto(p, e, n, iteration):")
content = content.replace("seed = dickson_v2_find_primitive_seed(p, m, n)", "seed = dickson_v2_find_primitive_seed(p, n)")
content = content.replace("dickson_v2_full_pipeline(p, e, m, seed, n)", "dickson_v2_full_pipeline(p, e, seed, n)")

# Update the calling loop
content = content.replace("times_auto.append(bench_v2_auto(p, e, m, n, i))", "times_auto.append(bench_v2_auto(p, e, n, i))")

# Remove sympy from contestant list and main loop
content = content.replace("times_sympy.append(bench_sympy(p, e, n, i))", "")
content = content.replace("'sympy':      trimmed_mean(times_sympy),", "")
content = content.replace("times_sympy = []", "")
content = content.replace('f"sympy={results[str(p)][\'sympy\']}"', '""')

with open("benchmark/runner_exp1_domain_vary_p.py", "w") as f:
    f.write(content)
