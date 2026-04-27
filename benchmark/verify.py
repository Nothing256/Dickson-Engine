import subprocess
import os
import re
import sympy as sp
from sympy.abc import x

# --- Configuration ---
DICKSON_BIN = "build/bin/dickson_bench"

def parse_traces(output):
    traces = {}
    for line in output.splitlines():
        match = re.search(r"Trace T\[(\d+)\] = (\d+)", line)
        if match:
            k = int(match.group(1))
            val = int(match.group(2))
            traces[k] = val
    return traces

def get_cosets(p, n):
    """Find all cyclotomic cosets mod n for p."""
    visited = set()
    cosets = []
    for i in range(1, n):
        if i not in visited:
            coset = []
            curr = i
            while curr not in visited:
                visited.add(curr)
                coset.append(curr)
                curr = (curr * p) % n
            cosets.append(coset)
    return cosets

def newton_girard(traces, m, p):
    """
    Convert power sums (traces) T_1..T_m into elementary symmetric polynomials e_1..e_m
    using Newton-Girard identities over GF(p).
    """
    e = [0] * (m + 1)
    e[0] = 1
    
    for k in range(1, m + 1):
        # k * e_k = \sum_{i=1}^k (-1)^{i-1} e_{k-i} T_i
        sum_val = 0
        for i in range(1, k + 1):
            term = (e[k - i] * traces[i]) % p
            if (i - 1) % 2 != 0:
                term = -term
            sum_val = (sum_val + term) % p
        
        # Divide by k in GF(p)
        k_inv = pow(k, p - 2, p)
        e[k] = (sum_val * k_inv) % p
        
    return e

def run_verification():
    print("\n=========================================================")
    print("=== Full MED Trace Product Verification: Dickson V2 ===")
    print("=========================================================")
    print("This script reads the sequence T_k from the Dickson Engine,")
    print("partitions them using MED (Multiple Equal-Difference) cosets,")
    print("reconstructs ALL factors G_s(X), and verifies their product")
    print("is EXACTLY X^n - 1 over GF(p).")
    
    if not os.path.exists(DICKSON_BIN):
        print("Error: Binaries not found. Please compile them first via 'make' in build/.")
        return

    test_cases = [
        (2, 7, 3),
        (3, 13, 3),
        (5, 31, 3),
        (7, 57, 3),
        (11, 133, 3)
    ]
    
    pass_count = 0
    fail_count = 0

    for p, n, m in test_cases:
        print(f"\n[Testing] p={p}, n={n} (m={m})")
        cmd = [DICKSON_BIN, str(p), "1", str(n), "--random"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            traces = parse_traces(result.stdout)
            
            # MED Cosets
            cosets = get_cosets(p, n)
            print(f"  > Identified {len(cosets)} non-trivial cyclotomic cosets.")
            
            total_product = sp.Poly(x - 1, x, domain=sp.GF(p))
            
            all_factors_valid = True
            for i, coset in enumerate(cosets):
                s = coset[0]
                # Extract MED traces for this coset: T_s, T_{2s}, ... T_{ms}
                med_traces = {}
                for k in range(1, m + 1):
                    idx = (s * k) % n
                    if idx == 0: idx = n
                    if idx not in traces:
                        # For k*s == n, T_n = m. Because roots are n-th roots of unity, alpha^n = 1.
                        # So sum_{j} (alpha^{n})^j = sum_{j} 1 = m.
                        med_traces[k] = m
                    else:
                        med_traces[k] = traces[idx]
                        
                # Newton Girard to find coefficients
                e = newton_girard(med_traces, m, p)
                
                # Construct polynomial G_s(X) = X^m - e_1 X^{m-1} + e_2 X^{m-2} ...
                G_expr = x**m
                for k in range(1, m + 1):
                    sign = -1 if k % 2 != 0 else 1
                    G_expr += sign * e[k] * x**(m - k)
                    
                G = sp.Poly(G_expr, x, domain=sp.GF(p))
                total_product = (total_product * G).trunc(p) # mod p multiplication
                
            # Verify if total_product == X^n - 1
            f_expr = x**n - 1
            f = sp.Poly(f_expr, x, domain=sp.GF(p))
            
            diff = (total_product - f).trunc(p)
            if diff.is_zero:
                print(f"  ✅ PASS: ∏ G_s(X) * (X-1) exactly equals X^{n} - 1 over GF({p})!")
                pass_count += 1
            else:
                print(f"  ❌ FAIL: Product does NOT equal X^{n} - 1. Diff: {diff}")
                fail_count += 1
                
        except subprocess.CalledProcessError:
            print(f"  ❌ FAIL: Engine crashed for p={p}, n={n}")
            fail_count += 1

    print("\n=========================================================")
    print(f"Verification Summary: {pass_count} Passed, {fail_count} Failed.")

if __name__ == "__main__":
    run_verification()
