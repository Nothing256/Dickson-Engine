"""
Dickson Engine V3 — Python Bignum Port

Extends V2 to handle the ramified case (p | n).
Uses Cyclotomic Substitution to lift unramified factors of X^m - 1
into ramified factors of X^{p^k m} - 1 via exact polynomial division.
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poly_arith import (
    poly_divmod, poly_trim, poly_degree, format_factorization
)
from dickson_v2 import (
    dickson_v2_full_pipeline, get_precomputed_seed, dickson_v2_find_primitive_seed
)


def poly_substitute_power(poly, power):
    """
    Substitute X with X^power in a polynomial.
    Returns G(X^power).
    """
    if not poly or (len(poly) == 1 and poly[0] == 0):
        return [0]
    
    degree = len(poly) - 1
    new_len = degree * power + 1
    res = [0] * new_len
    
    for i in range(len(poly)):
        res[i * power] = poly[i]
        
    return res


def dickson_v3_full_pipeline(p, e, n):
    """
    Run the complete V3 pipeline for X^n - 1 over Z_{p^e}.
    Handles both unramified (p \nmid n) and ramified (p | n) cases.
    """
    start_time = time.time()
    mod = p ** e

    # 1. Decompose n = p^k * m
    temp = n
    k = 0
    while temp % p == 0:
        k += 1
        temp //= p
    m = temp

    # 2. Factor the unramified core X^m - 1 using V2 Engine
    # Find multiplicative order of p mod m
    if m == 1:
        # X - 1 is the only factor
        unramified_factors = [[(mod - 1) % mod, 1]]
    else:
        m_order = 1
        curr = p % m
        while curr != 1 and m_order < m:
            curr = (curr * (p % m)) % m
            m_order += 1

        seed = get_precomputed_seed(p, m_order)
        if seed is None:
            seed = dickson_v2_find_primitive_seed(p, m)

        _, unramified_factors = dickson_v2_full_pipeline(p, e, seed, m)

    if k == 0:
        # Unramified case, V2 already did all the work
        elapsed = time.time() - start_time
        return elapsed, unramified_factors

    # 3. Cyclotomic Substitution Shortcut for Ramified Factors
    all_factors = []
    
    for G in unramified_factors:
        # G is a factor of X^m - 1
        all_factors.append(G)
        
        # Iteratively generate H_i^(j)(X) = G_i(X^{p^j}) / G_i(X^{p^{j-1}})
        for j in range(1, k + 1):
            G_top = poly_substitute_power(G, p ** j)
            G_bot = poly_substitute_power(G, p ** (j - 1))
            
            # Exact polynomial division over Z_{p^e}
            # Since G is monic, G_bot is also monic, so leading coeff is 1 (invertible)
            H, remainder = poly_divmod(G_top, G_bot, mod)
            
            # Verify exact division
            if poly_degree(remainder) > 0 or remainder[0] != 0:
                raise RuntimeError("V3 Substitution Division failed to be exact!")
                
            all_factors.append(H)

    elapsed = time.time() - start_time
    return elapsed, all_factors


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 dickson_v3.py <p> <e> <n>")
        sys.exit(1)

    p_val = int(sys.argv[1])
    e_val = int(sys.argv[2])
    n_val = int(sys.argv[3])

    elapsed_time, resulting_factors = dickson_v3_full_pipeline(p_val, e_val, n_val)
    
    print(f"Time Elapsed  : {elapsed_time:.6f}")
    print(f"Factor Count  : {len(resulting_factors)}")
    print(f"Factorization : {format_factorization(resulting_factors, p_val**e_val)}")
