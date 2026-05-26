"""
Dickson Engine V1 — Python Bignum Port

Ported from Dickson-Engine-1.0-isit/core/src/dickson.c

V1 is specialized for m=2 (quadratic Dickson recurrence):
    - Factorizes X^(p+1) - 1 over Z_{p^e}
    - Uses the Dickson polynomial V(x) of degree k = p//4
    - Hensel-lifts a scalar seed S from F_p to Z_{p^e}
    - Recovers generator A₁ via Newton square-root lifting
    - Generates all traces via D_i = A₁·D_{i-1} - D_{i-2}
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poly_arith import format_poly, format_factorization


def _binomial_coeff(n, k):
    """Compute binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n // 2:
        k = n - k
    res = 1
    for i in range(1, k + 1):
        res = res * (n - i + 1) // i
    return res


def dickson_v1_build_vx(p):
    """
    Build the coefficient array for the Dickson polynomial V(x).
    V(x) has degree k = p // 4.
    Coefficients are stored as [V_0, V_1, ..., V_k] where
    V(x) = V_0 * x^k + V_1 * x^{k-1} + ... + V_k
    (i.e., coeffs[r] is the coefficient of x^{k-r})
    """
    k = p // 4
    is_4k_plus_1 = (p % 4 == 1)
    coeffs = [0] * (k + 1)

    for r in range(k + 1):
        i = r // 2
        sign = 1 if (i % 2 == 0) else -1  # (-1)^i

        if r % 2 == 0:
            # V_{2i} = (-1)^i * C(k-i, i)
            binom = _binomial_coeff(k - i, i)
            coeffs[r] = sign * binom
        else:
            if not is_4k_plus_1:
                # p ≡ 3 (mod 4): V_{2i+1} = 0
                coeffs[r] = 0
            else:
                # p ≡ 1 (mod 4): V_{2i+1} = (-1)^{i+1} * C(k-i-1, i)
                sign2 = 1 if ((i + 1) % 2 == 0) else -1
                binom = _binomial_coeff(k - i - 1, i)
                coeffs[r] = sign2 * binom

    return coeffs, k


def _eval_v(coeffs, k, x, mod):
    """
    Evaluate V(x) mod m using Horner's method.
    coeffs[0]*x^k + coeffs[1]*x^{k-1} + ... + coeffs[k]
    """
    result = 0
    for r in range(k + 1):
        result = (result * x) % mod
        c = coeffs[r] % mod
        result = (result + c) % mod
    return result


def _eval_v_prime(coeffs, k, x, mod):
    """
    Evaluate V'(x) mod m using Horner's method.
    Derivative: for each term coeffs[r]*x^{k-r}, the derivative is
    coeffs[r]*(k-r)*x^{k-r-1}
    """
    result = 0
    for r in range(k):  # skip constant term (r=k)
        power = k - r
        result = (result * x) % mod
        c = (coeffs[r] * power) % mod
        result = (result + c) % mod
    return result


def _mod_inverse(a, m):
    """Extended Euclidean algorithm for modular inverse."""
    if m == 1:
        return 0
    g, x = _extended_gcd_simple(a % m, m)
    if g != 1:
        return None
    return x % m


def _extended_gcd_simple(a, b):
    """Returns (gcd, x) such that a*x ≡ gcd (mod b)."""
    if a == 0:
        return b, 0
    g, x = _extended_gcd_simple(b % a, a)
    return g, (1 - (b // a) * x) if g == 1 else (g, 0)


def _extended_gcd_full(a, b):
    """Full extended GCD: returns (g, x, y) with a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd_full(b % a, a)
    return g, y - (b // a) * x, x


def _mod_inverse_safe(a, m):
    """Compute modular inverse using full extended GCD."""
    g, x, _ = _extended_gcd_full(a % m, m)
    if g != 1:
        return None
    return x % m


def dickson_v1_lift_seed(p, e, s_base, coeffs, k):
    """
    Hensel-lift scalar seed S from mod p to mod p^e.

    At each step h (lifting from mod p^h to mod p^{h+1}):
        1. Compute V(s) mod p^{h+1}
        2. Delta = V(s) / p^h
        3. adjustment = C * Delta mod p (where C = -[V'(s)]^{-1} mod p)
        4. s_new = s + adjustment * p^h
    """
    # Pre-compute the invariant factor C = -[V'(s_base)]^-1 mod p
    v_prime = _eval_v_prime(coeffs, k, s_base, p)
    inv = _mod_inverse_safe(v_prime, p)
    if inv is None:
        raise ValueError("V'(s) is not invertible mod p — singular root")
    C = (p - inv) % p

    current_s = s_base
    current_p_pow = p  # p^1

    for h in range(1, e):
        next_mod = current_p_pow * p

        # Evaluate V(s) at higher precision
        v_val = _eval_v(coeffs, k, current_s, next_mod)

        # Delta = V(s) / p^h  (should be exactly divisible)
        delta = v_val // current_p_pow

        # Adjustment
        adjustment = (C * delta) % p

        # Update
        current_s = current_s + adjustment * current_p_pow
        current_p_pow = next_mod

    return current_s


def dickson_v1_recover_a(p, e, s_final, a_base):
    """
    Recover A₁ from S: solve A² = 2 - S (mod p^e) using Newton lifting.

    Newton iteration for square root:
        x_{k+1} = x_k - (x_k² - val) / (2*x_k)
    Only needs mod-p inverse at each step (Hensel property).
    """
    final_mod = p ** e
    val = (2 - s_final) % final_mod

    current_x = a_base % p
    current_mod = p

    for h in range(1, e):
        next_mod = current_mod * p

        x_sq = (current_x * current_x) % next_mod
        diff = (x_sq - val % next_mod) % next_mod
        if diff < 0:
            diff += next_mod

        den = (2 * current_x) % next_mod
        den_inv = _mod_inverse_safe(den % p, p)
        if den_inv is None:
            raise ValueError("Newton lift: denominator not invertible")

        # diff should be divisible by current_mod
        diff_scaled = diff // current_mod
        adjustment_factor = (diff_scaled * den_inv) % p
        adjustment = (p - adjustment_factor) % p

        current_x = current_x + adjustment * current_mod
        current_mod = next_mod

    return current_x % final_mod


def dickson_v1_reconstruct_factors(p, e, a1):
    """
    Reconstruct all factors of X^(p+1) - 1 over Z_{p^e} from generator A₁.

    V1 produces:
      - (x - 1) and (x + 1)  (always)
      - (x² + 1)             (only when p ≡ 3 mod 4)
      - k pairs of quadratic factors via Dickson recurrence:
          (x² - D_i·x + 1) and (x² + D_i·x + 1)  for i = 1..k

    Returns list of factor polynomials as coefficient lists [a0, a1, ..., an].
    """
    mod = p ** e
    k = p // 4

    factors = []

    # Fixed factors
    factors.append([(mod - 1) % mod, 1])     # (x - 1)
    factors.append([1, 1])                    # (x + 1)
    if p % 4 == 3:
        factors.append([1, 0, 1])             # (x² + 1)

    # Dickson recurrence: D_1 = A₁, D_i = A₁·D_{i-1} - D_{i-2}
    d_prev = 2
    d_curr = a1

    for i in range(1, k + 1):
        neg_d = (mod - d_curr) % mod
        factors.append([1, neg_d, 1])  # (x² - D_i·x + 1)
        factors.append([1, d_curr, 1]) # (x² + D_i·x + 1)

        if i < k:
            d_next = (a1 * d_curr - d_prev) % mod
            d_prev = d_curr
            d_curr = d_next

    return factors


def dickson_v1_full_pipeline(p, e, a_base):
    """
    Run the complete V1 pipeline (end-to-end, matching SageMath's scope):
        1. Build V(x) coefficients
        2. Compute s_base = (2 - a_base²) mod p
        3. Lift s_base → s_final (mod p^e)
        4. Recover A₁ from s_final
        5. Reconstruct all factors via Dickson recurrence

    Returns (elapsed_time, factors).
    factors = list of coefficient lists [[a0, a1, ...], ...]
    The timer covers steps 2-5 (excluding V(x) construction, which is
    a one-time precomputation independent of e).
    """
    coeffs, k = dickson_v1_build_vx(p)

    start = time.time()

    # Step 2: Compute s_base
    a1_sq = (a_base * a_base) % p
    s_base = (2 - a1_sq) % p

    # Step 3: Lift seed
    s_final = dickson_v1_lift_seed(p, e, s_base, coeffs, k)

    # Step 4: Recover A₁
    a1 = dickson_v1_recover_a(p, e, s_final, a_base)

    # Step 5: Reconstruct factors
    factors = dickson_v1_reconstruct_factors(p, e, a1)

    elapsed = time.time() - start
    return elapsed, factors


# --- Seed Finding (for precomputation) ---

def dickson_v1_find_seed(p):
    """
    Find a valid seed A for V1: must satisfy that x² - Ax + 1 is
    irreducible over F_p (i.e., discriminant A²-4 is a quadratic non-residue).
    """
    import random
    for _ in range(10000):
        a = random.randint(1, p - 1)
        D = (a * a - 4) % p
        if D == 0:
            continue
        # Legendre symbol check: D^{(p-1)/2} must be p-1 (i.e., -1)
        if pow(D, (p - 1) // 2, p) == p - 1:
            return a
    raise RuntimeError(f"Could not find valid V1 seed for p={p}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 dickson_v1.py <p> <e> [seed]")
        sys.exit(1)

    p = int(sys.argv[1])
    e = int(sys.argv[2])
    mod = p ** e

    if len(sys.argv) >= 4:
        seed = int(sys.argv[3])
    else:
        seed = dickson_v1_find_seed(p)
        print(f"Auto-found seed: {seed}")

    elapsed, factors = dickson_v1_full_pipeline(p, e, seed)
    print(f"Time Elapsed  : {elapsed:.6f}")
    print(f"Factor Count  : {len(factors)}")
    print(f"Factorization : {format_factorization(factors, mod)}")
