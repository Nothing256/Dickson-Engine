"""
Polynomial Arithmetic over Z_m (Arbitrary Precision)

Ported from core/src/poly_alg.c to Python for bignum support.
Polynomials are represented as lists of coefficients:
    [a0, a1, ..., an]  where p(x) = a0 + a1*x + ... + an*x^n
"""


def poly_trim(p):
    """Remove trailing zero coefficients (normalize degree)."""
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def poly_degree(p):
    """Return the degree of polynomial p."""
    return len(p) - 1


def poly_add(a, b, mod):
    """Add two polynomials modulo mod."""
    n = max(len(a), len(b))
    result = [0] * n
    for i in range(len(a)):
        result[i] = (result[i] + a[i]) % mod
    for i in range(len(b)):
        result[i] = (result[i] + b[i]) % mod
    return poly_trim(result)


def poly_sub(a, b, mod):
    """Subtract polynomial b from a, modulo mod."""
    n = max(len(a), len(b))
    result = [0] * n
    for i in range(len(a)):
        result[i] = (result[i] + a[i]) % mod
    for i in range(len(b)):
        result[i] = (result[i] - b[i]) % mod
    return poly_trim(result)


def poly_mul(a, b, mod):
    """Multiply two polynomials modulo mod."""
    if not a or not b:
        return [0]
    n = len(a) + len(b) - 1
    result = [0] * n
    for i in range(len(a)):
        if a[i] == 0:
            continue
        for j in range(len(b)):
            result[i + j] = (result[i + j] + a[i] * b[j]) % mod
    return poly_trim(result)


def poly_scalar_mul(a, scalar, mod):
    """Multiply polynomial a by a scalar, modulo mod."""
    return poly_trim([(c * scalar) % mod for c in a])


def int_mod_inverse(a, m):
    """
    Compute modular inverse of integer a modulo m.
    Returns None if inverse does not exist.
    """
    if m == 1:
        return 0
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m


def _extended_gcd(a, b):
    """Extended Euclidean Algorithm: returns (gcd, x, y) such that a*x + b*y = gcd."""
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def poly_divmod(a, b, mod):
    """
    Polynomial Euclidean division: a = b * q + r
    Returns (quotient, remainder).
    Requires leading coefficient of b to be invertible modulo mod.
    """
    if not b or (len(b) == 1 and b[0] == 0):
        raise ValueError("Division by zero polynomial")

    a = list(a)  # copy
    deg_a = len(a) - 1
    deg_b = len(b) - 1

    if deg_a < deg_b:
        return [0], poly_trim(a)

    lc_b = b[-1] % mod
    lc_b_inv = int_mod_inverse(lc_b, mod)
    if lc_b_inv is None:
        raise ValueError(f"Leading coefficient {lc_b} not invertible mod {mod}")

    q = [0] * (deg_a - deg_b + 1)

    for i in range(deg_a - deg_b, -1, -1):
        coeff = (a[i + deg_b] * lc_b_inv) % mod
        q[i] = coeff
        for j in range(deg_b + 1):
            a[i + j] = (a[i + j] - coeff * b[j]) % mod

    return poly_trim(q), poly_trim(a)


def poly_mod(a, b, mod):
    """Compute a mod b (polynomial remainder), modulo mod."""
    _, r = poly_divmod(a, b, mod)
    return r


def poly_ext_gcd(a, b, p):
    """
    Extended GCD for polynomials over Z_p.
    Returns (gcd, x, y) such that a*x + b*y = gcd (mod p).
    """
    if len(a) == 1 and a[0] == 0:
        return list(b), [0], [1]

    _, r = poly_divmod(b, a, p)
    q, _ = poly_divmod(b, a, p)

    g, x, y = poly_ext_gcd(r, a, p)

    # new_x = y - q * x
    qx = poly_mul(q, x, p)
    new_x = poly_sub(y, qx, p)

    return g, new_x, x


def poly_mod_inverse(a, m, p):
    """
    Compute the multiplicative inverse of polynomial a modulo polynomial m,
    over Z_p. Returns None if inverse does not exist.
    """
    g, x, _ = poly_ext_gcd(a, m, p)

    # Check that gcd is a nonzero constant (degree 0)
    gt = poly_trim(list(g))
    if poly_degree(gt) != 0 or gt[0] == 0:
        return None

    # Normalize: multiply x by g[0]^-1
    g_inv = int_mod_inverse(gt[0], p)
    if g_inv is None:
        return None

    result = poly_scalar_mul(x, g_inv, p)
    result = poly_mod(result, m, p)
    return poly_trim(result)


def poly_mod_pow(base, exp, mod_poly, p):
    """
    Fast modular exponentiation for polynomials:
    Compute base^exp mod mod_poly, over Z_p.
    Uses binary square-and-multiply.
    """
    if exp == 0:
        return [1]

    result = [1]
    b = poly_mod(list(base), mod_poly, p)

    while exp > 0:
        if exp & 1:
            result = poly_mul(result, b, p)
            result = poly_mod(result, mod_poly, p)
        b = poly_mul(b, b, p)
        b = poly_mod(b, mod_poly, p)
        exp >>= 1

    return poly_trim(result)
