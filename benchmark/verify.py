import subprocess
import os
import re
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# --- Configuration ---
DICKSON_BIN = "build/bin/dickson_bench"

# SymPy parsing transformations to handle expressions like "34x" as "34*x"
transformations = standard_transformations + (implicit_multiplication_application,)
x = sp.Symbol('x')

def parse_poly(expr_str):
    """
    Parses a string like 'x^2 - 29x + 1' into a SymPy Polynomial over ZZ.
    """
    expr_str = expr_str.replace("^", "**")
    expr = parse_expr(expr_str, transformations=transformations)
    return sp.Poly(expr, x, domain='ZZ')

def run_verification():
    print("\n=========================================================")
    print("=== Dickson V2 Full Acceptance Verification Suite ===")
    print("=========================================================")
    print("This script reads the explicit polynomial factorization output")
    print("from the Dickson Engine C binary, parses them into SymPy objects,")
    print("and mathematically verifies that their expanded product matches")
    print("X^n - 1 modulo p^e (covering both fields and lifted rings).")
    
    if not os.path.exists(DICKSON_BIN):
        print("Error: Binaries not found. Please compile them first via 'make' in build/.")
        return

    # Test cases: (p, e, n)
    test_cases = [
        # Base Fields (GF(p))
        (2, 1, 7),     # Degenerate coset due to p <= m (m=3)
        (3, 1, 13),    # Base field GF(3)
        (5, 1, 31),    # Base field GF(5)
        (197, 1, 39007), # Large base field
        
        # Lifted Rings (Z_{p^e})
        (13, 2, 14),   # Ring Z_{169}
        (3, 3, 13),    # Ring Z_{27}
        (5, 2, 31),    # Ring Z_{25}
        (2, 3, 7)      # Ring Z_{8} with degenerate coset
    ]
    
    pass_count = 0
    fail_count = 0
    skip_count = 0

    for p, e, n in test_cases:
        print(f"\n[Testing] p={p}, e={e}, n={n} (Modulus: {p**e})")
        
        cmd = [DICKSON_BIN, str(p), str(e), str(n), "--random"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Parse Factors
            factors = []
            parsing_factors = False
            for line in output.splitlines():
                if "Full Factorization" in line:
                    parsing_factors = True
                    continue
                if parsing_factors:
                    if line.startswith("Total Factors:"):
                        break
                    match = re.match(r"^\[\d+\] \((.*)\)$", line.strip())
                    if match:
                        factor_str = match.group(1)
                        factors.append(factor_str)
            
            if not factors:
                print("  ❌ FAIL: No factors parsed from engine output.")
                fail_count += 1
                continue
                
            print(f"  > Engine returned {len(factors)} factors. Multiplying over ZZ...")
            
            # Parse all polynomials first
            parsed_factors = []
            for f_str in factors:
                parsed_factors.append(parse_poly(f_str))
                
            # Tree-based multiplication over ZZ with modulo reduction
            # This reduces O(N^2) complexity to O(N log N) for massive polynomial products
            modulus = p**e
            current_layer = parsed_factors
            layer_count = 0
            
            while len(current_layer) > 1:
                next_layer = []
                for i in range(0, len(current_layer), 2):
                    if i + 1 < len(current_layer):
                        prod = (current_layer[i] * current_layer[i+1]).trunc(modulus)
                        next_layer.append(prod)
                    else:
                        next_layer.append(current_layer[i])
                current_layer = next_layer
                layer_count += 1
                if len(parsed_factors) > 1000:
                    print(f"    ... tree multiplication layer {layer_count} complete (reduced to {len(current_layer)} polys) ...")
                    
            total_product = current_layer[0]
                
            # Verify: (Product) - (X^n - 1) == 0 mod p^e
            target = sp.Poly(x**n - 1, x, domain='ZZ').trunc(modulus)
            diff = (total_product - target).trunc(modulus)
            
            # Check if all coefficients of the difference are 0
            is_valid = all(c == 0 for c in diff.coeffs())
                    
            if is_valid:
                print(f"  ✅ PASS: ∏ G_s(X) exactly equals X^{n} - 1 over Z_{modulus}!")
                pass_count += 1
            else:
                print(f"  ❌ FAIL: Product does NOT equal X^{n} - 1 modulo {modulus}.")
                print(f"     Difference polynomial: {diff}")
                fail_count += 1
                
        except subprocess.CalledProcessError:
            print(f"  ❌ FAIL: Engine crashed for p={p}, e={e}, n={n}")
            fail_count += 1

    print("\n=========================================================")
    print(f"Verification Summary: {pass_count} Passed, {fail_count} Failed, {skip_count} Skipped.")

if __name__ == "__main__":
    run_verification()
