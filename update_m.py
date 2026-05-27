import sys

with open("python/dickson_v2.py", "r") as f:
    content = f.read()

# Replace find_primitive_seed signature
content = content.replace("def dickson_v2_find_primitive_seed(p, m, n_val):", """def dickson_v2_find_primitive_seed(p, n_val):
    \"\"\"
    Find a primitive seed polynomial G(x) over F_p.
    Computes m = ord_n(p) internally.
    Uses random search with integrity checks (O(log n) verification).
    \"\"\"
    m = 1
    curr = p % n_val
    while curr != 1 and m <= n_val:
        curr = (curr * p) % n_val
        m += 1
    if m > n_val:
        raise RuntimeError(f"Could not compute m for p={p}, n={n_val}")""")
content = content.replace('    """\n    Find a primitive seed polynomial G(x) of degree m over F_p.\n    Uses random search with integrity checks (O(log n) verification).\n    """', "")

# Replace full_pipeline signature
content = content.replace("def dickson_v2_full_pipeline(p, e, m, G_base, n_val):", """def dickson_v2_full_pipeline(p, e, G_base, n_val):""")
content = content.replace("G_lifted = dickson_v2_algebraic_lift(p, e, m, G_base, n_val)", "m = len(G_base) - 1\n    G_lifted = dickson_v2_algebraic_lift(p, e, m, G_base, n_val)")

# Replace main block
content = content.replace("seed = dickson_v2_find_primitive_seed(p, m, n)", "seed = dickson_v2_find_primitive_seed(p, n)")
content = content.replace("elapsed, factors = dickson_v2_full_pipeline(p, e, m, seed, n)", "elapsed, factors = dickson_v2_full_pipeline(p, e, seed, n)")

with open("python/dickson_v2.py", "w") as f:
    f.write(content)
