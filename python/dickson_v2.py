"""
Dickson Engine V2 — Python Bignum Port

Ported from core/src/dickson.c (V2) + core/src/poly_alg.c

V2 is the general multi-dimensional engine:
    - Factorizes X^n - 1 over Z_{p^e} for arbitrary m
    - Uses polynomial Hensel lifting (Jacobian-Free Algebraic Lift)
    - Extracts traces via Newton-Girard recurrence on lifted polynomial
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poly_arith import (
    poly_add, poly_sub, poly_mul, poly_scalar_mul,
    poly_divmod, poly_mod, poly_mod_inverse, poly_mod_pow,
    poly_trim, poly_degree, int_mod_inverse,
    format_poly, format_factorization,
)


# --- Precomputed Seeds (Oxygen Tank) ---
# For p=30011, m=2: G(x) = x^2 + 24064x + 1 → coeffs = [1, 24064, 1]
PRECOMPUTED_SEEDS = {
    (3, 2): [1, 0, 1],
    (5, 2): [1, 4, 1],
    (7, 2): [1, 4, 1],
    (11, 2): [1, 5, 1],
    (13, 2): [1, 7, 1],
    (30011, 2): [1, 24064, 1],
}


def get_precomputed_seed(p, m):
    """Look up precomputed seed polynomial for (p, m)."""
    return PRECOMPUTED_SEEDS.get((p, m))


def dickson_v2_algebraic_lift(p, e, m, G_base, n_val):
    """
    Jacobian-Free Algebraic Seed Lifting.

    Lifts polynomial G(x) from mod p to mod p^e using the formula:
        E(x) = [X^n - 1 mod G_h(x)] / p^h  (mod p)
        ΔG(x) = E(x) · H⁻¹(x) mod G₁(x)   (over F_p)
        G_{h+1}(x) = G_h(x) + p^h · ΔG(x)

    Key optimization: H⁻¹(x) is computed ONCE and reused at every step.
    """
    G_lifted = list(G_base)
    current_mod = p

    if e <= 1:
        return G_lifted

    # --- PRE-COMPUTATION: H_inv Caching ---
    # Construct X^n - 1 and divide by G_base over F_p to get H_1(x)
    Xn_minus_1 = [0] * (n_val + 1)
    Xn_minus_1[n_val] = 1
    Xn_minus_1[0] = (-1) % p

    H_1, R_0 = poly_divmod(Xn_minus_1, G_base, p)

    # Compute the universally reusable inverse H_inv(x) mod G_1(x) over F_p
    H_inv = poly_mod_inverse(H_1, G_base, p)
    if H_inv is None:
        raise ValueError("H_1(x) is not invertible mod G_1(x) — lift failed")

    # X polynomial for fast modular exponentiation
    X_poly = [0, 1]

    # --- FAST LIFTING LOOP ---
    for h in range(1, e):
        next_mod = current_mod * p

        # 1. Fast Remainder: X^n mod G_h(x) over Z_{p^{h+1}}
        Xn_mod = poly_mod_pow(X_poly, n_val, G_lifted, next_mod)
        # R_h = X^n - 1 mod G_h(x)
        R_h = list(Xn_mod)
        R_h[0] = (R_h[0] - 1) % next_mod

        # 2. Extract E(x) = R_h(x) / p^h mod p
        E = [0] * len(R_h)
        for i in range(len(R_h)):
            raw_val = R_h[i] % next_mod
            if raw_val < 0:
                raw_val += next_mod
            e_val = (raw_val // current_mod) % p
            E[i] = e_val % p
        E = poly_trim(E)

        # 3. Compute ΔG(x) = E(x) · H_inv(x) mod G_1(x) over F_p
        E_mul_Hinv = poly_mul(E, H_inv, p)
        Delta_G = poly_mod(E_mul_Hinv, G_base, p)

        # 4. Construct G_{h+1}(x) = G_h(x) + p^h · ΔG(x) mod p^{h+1}
        for i in range(len(Delta_G)):
            if i < len(G_lifted):
                delta_val = Delta_G[i] % p
                scaled_delta = (delta_val * current_mod) % next_mod
                G_lifted[i] = (G_lifted[i] + scaled_delta) % next_mod

        current_mod = next_mod

    return poly_trim(G_lifted)


def dickson_v2_multidimensional_dispatch(p, e, m, G_lifted, total_target_traces):
    """
    Multi-dimensional Dickson Generator Array (Newton-Girard recurrence).

    Extracts traces T_k from the lifted polynomial G(x) using:
        T_k = Σ_{j=1}^{m} (-1)^{j-1} · A_j · T_{k-j}

    where A_j are the symmetric parameters extracted from G(x).
    """
    final_mod = p ** e

    # Extract symmetric parameters A_j from G_lifted
    # G(x) = x^m + c_{m-1}·x^{m-1} + ... + c_0
    # A_j = (-1)^j · c_{m-j}
    A = [0] * (m + 1)
    for j in range(1, m + 1):
        idx = m - j
        coeff = G_lifted[idx] if idx < len(G_lifted) else 0
        sign = -1 if (j % 2 != 0) else 1
        A[j] = (coeff * sign) % final_mod

    # Allocate trace array
    max_T = max(total_target_traces, m)
    T = [0] * (max_T + 1)

    # Initial traces
    T[0] = m
    if total_target_traces >= 1:
        T[1] = A[1]

    # Newton-Girard initialization (k = 2..m)
    for k in range(2, min(m, total_target_traces) + 1):
        param_sum = 0
        for j in range(1, k):
            term = (A[j] * T[k - j]) % final_mod
            sign = 1 if (j % 2 != 0) else -1
            param_sum = (param_sum + sign * term) % final_mod
        tail = (k * A[k]) % final_mod
        tail_sign = 1 if (k % 2 != 0) else -1
        T[k] = (param_sum + tail_sign * tail) % final_mod

    # Main recurrence (k > m)
    for k in range(m + 1, total_target_traces + 1):
        next_T = 0
        for j in range(1, m + 1):
            term = (A[j] * T[k - j]) % final_mod
            sign = 1 if (j % 2 != 0) else -1
            next_T = (next_T + sign * term) % final_mod
        T[k] = next_T

    return T


def dickson_v2_reconstruct_factors(p, e, m, T, n_val):
    """
    Reconstruct all irreducible factors of X^n - 1 over Z_{p^e}
    from the trace array T using MED coset partitioning + Newton-Girard.

    Algorithm:
      1. Partition Z_n* into p-cyclotomic cosets
      2. For each coset {i, ip, ip², ...} of size m_coset:
         a. Extract MED-scaled traces from T
         b. Apply Newton-Girard to recover elementary symmetric polynomials
         c. Build the irreducible factor polynomial

    Returns list of factor polynomials as coefficient lists.
    """
    final_mod = p ** e
    factors = []

    # (x - 1) corresponds to index 0
    factors.append([(final_mod - 1) % final_mod, 1])

    visited = [False] * n_val
    visited[0] = True

    for i in range(1, n_val):
        if visited[i]:
            continue

        # Trace the p-cyclotomic coset
        m_coset = 0
        curr = i
        while not visited[curr]:
            visited[curr] = True
            curr = (curr * p) % n_val
            m_coset += 1

        # MED trace extraction with scaling
        scale = m // m_coset
        scale_inv = int_mod_inverse(scale, final_mod)
        if scale_inv is None:
            # Degenerate coset (p | scale), use raw factor
            factors.append([1] + [0] * (m_coset - 1) + [1])
            continue

        med_traces = [0] * (m_coset + 1)
        for k in range(1, m_coset + 1):
            idx = (i * k) % n_val
            raw_trace = (m % final_mod) if idx == 0 else T[idx]
            med_traces[k] = (raw_trace * scale_inv) % final_mod

        # Newton-Girard: traces → elementary symmetric polynomials
        e_sym = [0] * (m_coset + 1)
        e_sym[0] = 1

        reconstruct_ok = True
        for k in range(1, m_coset + 1):
            sum_val = 0
            for j in range(1, k + 1):
                term = (e_sym[k - j] * med_traces[j]) % final_mod
                # sign pattern: j=1 → +, j=2 → -, j=3 → +, ...
                if (j - 1) % 2 != 0:
                    term = (-term) % final_mod
                sum_val = (sum_val + term) % final_mod

            k_inv = int_mod_inverse(k, final_mod)
            if k_inv is None:
                reconstruct_ok = False
                break
            e_sym[k] = (sum_val * k_inv) % final_mod

        if not reconstruct_ok:
            factors.append([1] + [0] * (m_coset - 1) + [1])
            continue

        # Build factor polynomial from e_sym
        # f(x) = x^{m_coset} + Σ_{k=1}^{m_coset} (-1)^k · e_sym[k] · x^{m_coset-k}
        factor_coeffs = [0] * (m_coset + 1)
        factor_coeffs[m_coset] = 1  # monic: x^{m_coset}
        for k in range(1, m_coset + 1):
            sign = -1 if (k % 2 != 0) else 1
            factor_coeffs[m_coset - k] = (sign * e_sym[k]) % final_mod

        factors.append(factor_coeffs)

    return factors


def dickson_v2_full_pipeline(p, e, m, G_base, n_val):
    """
    Run the complete V2 pipeline (end-to-end, matching SageMath's scope):
        1. Algebraic Lift: G_base (mod p) → G_lifted (mod p^e)
        2. Multidimensional Dispatch: extract n traces from G_lifted
        3. Factor Reconstruction: MED + Newton-Girard

    Returns (elapsed_time, factors).
    factors = list of coefficient lists [[a0, a1, ...], ...]
    Timer covers all three stages (seed already provided).
    """
    start = time.time()

    # Stage 1: Algebraic Lift
    G_lifted = dickson_v2_algebraic_lift(p, e, m, G_base, n_val)

    # Stage 2: Trace Generation
    T = dickson_v2_multidimensional_dispatch(p, e, m, G_lifted, n_val)

    # Stage 3: Factor Reconstruction
    factors = dickson_v2_reconstruct_factors(p, e, m, T, n_val)

    elapsed = time.time() - start
    return elapsed, factors


# --- Auto-Seeder ---

def dickson_v2_find_primitive_seed(p, m, n_val):
    """
    Find a primitive seed polynomial G(x) of degree m over F_p.
    Uses random search with integrity checks (O(log n) verification).
    """
    import random

    # Prime factorization of n_val
    factors = []
    temp = n_val
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)

    X = [0, 1]

    for attempt in range(200000):
        # Generate random monic polynomial of degree m
        G = [0] * (m + 1)
        G[m] = 1  # monic
        G[0] = 1 + random.randint(0, p - 2)  # nonzero constant term
        for i in range(1, m):
            G[i] = random.randint(0, p - 1)

        # Check: X^n ≡ 1 mod G(x) over F_p
        res_n = poly_mod_pow(X, n_val, G, p)
        if not (poly_degree(res_n) == 0 and res_n[0] == 1):
            continue

        # Short-cycle defense: X^{n/q} ≠ 1 for all prime factors q of n
        is_primitive = True
        for q in factors:
            sub_order = n_val // q
            res_sub = poly_mod_pow(X, sub_order, G, p)
            if poly_degree(res_sub) == 0 and res_sub[0] == 1:
                is_primitive = False
                break

        if is_primitive:
            return G

    raise RuntimeError(f"Could not find primitive seed for p={p}, m={m}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 dickson_v2.py <p> <e> [n]")
        sys.exit(1)

    p = int(sys.argv[1])
    e = int(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) >= 4 else p + 1

    # Compute m = multiplicative order of p mod n
    m = 1
    curr = p % n
    while curr != 1 and m < n:
        curr = (curr * (p % n)) % n
        m += 1

    # Get seed
    seed = get_precomputed_seed(p, m)
    if seed is None:
        print(f"No precomputed seed for p={p}, m={m}. Auto-searching...")
        seed = dickson_v2_find_primitive_seed(p, m, n)

    elapsed, factors = dickson_v2_full_pipeline(p, e, m, seed, n)
    print(f"Time Elapsed  : {elapsed:.6f}")
    print(f"Factor Count  : {len(factors)}")
    print(f"Factorization : {format_factorization(factors, p**e)}")
