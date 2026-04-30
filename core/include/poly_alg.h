#ifndef POLY_ALG_H
#define POLY_ALG_H

#include <stdlib.h>
#include <stdio.h>

// Assuming long long for simplicity representing Z_p^e arrays
typedef long long poly_int;

typedef struct {
    int degree;      // Highest exponent
    poly_int *coeffs; // Array of coefficients of size degree + 1 (index corresponds to power i)
} Poly;

// Poly memory management
Poly* poly_create(int degree);
void poly_free(Poly *p);
Poly* poly_copy(const Poly *p);

// Polynomial arithmetic modulo m
Poly* poly_add(const Poly *a, const Poly *b, poly_int mod);
Poly* poly_sub(const Poly *a, const Poly *b, poly_int mod);
Poly* poly_mul(const Poly *a, const Poly *b, poly_int mod);
Poly* poly_scalar_mul(const Poly *a, poly_int scaler, poly_int mod);

// Euclidean division: Returns Remainder, optionally computes quotient if q is not NULL
// A = B * Q + R
// Returns R. Must ensure leading coeff of B is invertible mod (usually it's 1 for monic).
Poly* poly_div_rem(const Poly *a, const Poly *b, Poly **q, poly_int mod);

// Extended Euclidean Algorithm: Returns gcd(A, B) and optionally sets X and Y such that A*X + B*Y = gcd(A, B)
Poly* poly_ext_gcd(const Poly *a, const Poly *b, Poly **x_out, Poly **y_out, poly_int p);

// Multiplicative inverse of a polynomial A modulo M
Poly* poly_mod_inverse(const Poly *a, const Poly *m, poly_int p);

// Fast polynomial exponentiation: base^exp % mod_poly over Z_p
Poly* poly_mod_pow(const Poly *base, poly_int exp, const Poly *mod_poly, poly_int p);

// Solve linear system over Z_{p^e}
int solve_linear_system(poly_int **matrix, int rows, int cols, poly_int mod, poly_int p, poly_int *solution);

void poly_print(const Poly *p);

#endif // POLY_ALG_H
