#include "poly_alg.h"

// Modulo helper handling negative numbers natively
static poly_int mod_val(poly_int a, poly_int m) {
    poly_int r = a % m;
    if (r < 0) r += m;
    return r;
}

static poly_int mod_inverse(poly_int a, poly_int m) {
    poly_int t = 0, newt = 1;
    poly_int r = m, newr = a;
    while (newr != 0) {
        poly_int quotient = r / newr;
        poly_int temp = t - quotient * newt;
        t = newt; newt = temp;
        temp = r - quotient * newr;
        r = newr; newr = temp;
    }
    if (r > 1) return 0; // Not invertible
    if (t < 0) t += m;
    return t;
}

Poly* poly_create(int degree) {
    if (degree < 0) degree = 0;
    Poly *p = (Poly*)malloc(sizeof(Poly));
    p->degree = degree;
    p->coeffs = (poly_int*)calloc(degree + 1, sizeof(poly_int));
    return p;
}

void poly_free(Poly *p) {
    if (p) {
        free(p->coeffs);
        free(p);
    }
}

Poly* poly_copy(const Poly *p) {
    Poly *n = poly_create(p->degree);
    for (int i = 0; i <= p->degree; i++) {
        n->coeffs[i] = p->coeffs[i];
    }
    return n;
}

static void poly_trim(Poly **pp) {
    Poly *p = *pp;
    int actual_deg = p->degree;
    while (actual_deg > 0 && p->coeffs[actual_deg] == 0) {
        actual_deg--;
    }
    if (actual_deg < p->degree) {
        Poly *trimmed = poly_create(actual_deg);
        for(int i=0; i<=actual_deg; i++) trimmed->coeffs[i] = p->coeffs[i];
        poly_free(p);
        *pp = trimmed;
    }
}

Poly* poly_add(const Poly *a, const Poly *b, poly_int mod) {
    int max_deg = a->degree > b->degree ? a->degree : b->degree;
    Poly *res = poly_create(max_deg);
    for(int i = 0; i <= max_deg; i++) {
        poly_int val_a = (i <= a->degree) ? a->coeffs[i] : 0;
        poly_int val_b = (i <= b->degree) ? b->coeffs[i] : 0;
        res->coeffs[i] = mod_val(val_a + val_b, mod);
    }
    poly_trim(&res);
    return res;
}

Poly* poly_sub(const Poly *a, const Poly *b, poly_int mod) {
    int max_deg = a->degree > b->degree ? a->degree : b->degree;
    Poly *res = poly_create(max_deg);
    for(int i = 0; i <= max_deg; i++) {
        poly_int val_a = (i <= a->degree) ? a->coeffs[i] : 0;
        poly_int val_b = (i <= b->degree) ? b->coeffs[i] : 0;
        res->coeffs[i] = mod_val(val_a - val_b, mod);
    }
    poly_trim(&res);
    return res;
}

Poly* poly_scalar_mul(const Poly *a, poly_int scaler, poly_int mod) {
    Poly *res = poly_create(a->degree);
    for(int i = 0; i <= a->degree; i++) {
        res->coeffs[i] = mod_val(a->coeffs[i] * scaler, mod);
    }
    poly_trim(&res);
    return res;
}

Poly* poly_mul(const Poly *a, const Poly *b, poly_int mod) {
    Poly *res = poly_create(a->degree + b->degree);
    for(int i = 0; i <= a->degree; i++) {
        for(int j = 0; j <= b->degree; j++) {
            poly_int term = mod_val(a->coeffs[i] * b->coeffs[j], mod);
            res->coeffs[i+j] = mod_val(res->coeffs[i+j] + term, mod);
        }
    }
    poly_trim(&res);
    return res;
}

// Polynomial euclidean division modulo m
Poly* poly_div_rem(const Poly *A, const Poly *B, Poly **Q_out, poly_int mod) {
    if (B->degree == 0 && B->coeffs[0] == 0) return NULL; // Div by zero
    
    Poly *R = poly_copy(A);
    Poly *Q = poly_create(A->degree >= B->degree ? A->degree - B->degree : 0);
    
    poly_int lead_B = B->coeffs[B->degree];
    poly_int lead_inv = mod_inverse(lead_B, mod);
    
    if (B->degree == 0) {
        for (int i = 0; i <= R->degree; i++) {
            Q->coeffs[i] = mod_val(R->coeffs[i] * lead_inv, mod);
            R->coeffs[i] = 0;
        }
        poly_trim(&R);
        poly_trim(&Q);
        if (Q_out) *Q_out = Q; else poly_free(Q);
        return R;
    }
    
    while (R->degree >= B->degree) {
        if (R->degree == 0 && R->coeffs[0] == 0) break;
        if (R->coeffs[R->degree] == 0) {
            poly_trim(&R);
            continue;
        }
        int deg_diff = R->degree - B->degree;
        poly_int factor = mod_val(R->coeffs[R->degree] * lead_inv, mod);
        
        Q->coeffs[deg_diff] = factor;
        
        // Subtract factor * x^deg_diff * B from R
        for (int i = 0; i <= B->degree; i++) {
            poly_int sub_val = mod_val(factor * B->coeffs[i], mod);
            R->coeffs[i + deg_diff] = mod_val(R->coeffs[i + deg_diff] - sub_val, mod);
        }
        poly_trim(&R);
    }
    
    poly_trim(&Q);
    if (Q_out) {
        *Q_out = Q;
    } else {
        poly_free(Q);
    }
    return R;
}

// Extended Euclidean Algorithm for polynomials over Z_p
// Returns gcd(a, b). Sets x_out and y_out such that a*x + b*y = gcd(a, b)
Poly* poly_ext_gcd(const Poly *a, const Poly *b, Poly **x_out, Poly **y_out, poly_int p) {
    Poly *old_r = poly_copy(a);
    Poly *r = poly_copy(b);
    Poly *old_s = poly_create(0); old_s->coeffs[0] = 1;
    Poly *s = poly_create(0);
    Poly *old_t = poly_create(0);
    Poly *t = poly_create(0); t->coeffs[0] = 1;

    while (r->degree > 0 || r->coeffs[0] != 0) {
        Poly *q = NULL;
        Poly *rem = poly_div_rem(old_r, r, &q, p);
        
        poly_free(old_r);
        old_r = r;
        r = rem;

        Poly *qs = poly_mul(q, s, p);
        Poly *new_s = poly_sub(old_s, qs, p);
        poly_free(old_s);
        old_s = s;
        s = new_s;
        poly_free(qs);

        Poly *qt = poly_mul(q, t, p);
        Poly *new_t = poly_sub(old_t, qt, p);
        poly_free(old_t);
        old_t = t;
        t = new_t;
        poly_free(qt);

        poly_free(q);
    }

    poly_free(r);
    poly_free(s);
    poly_free(t);

    // Make monic
    if (old_r->degree >= 0 && old_r->coeffs[old_r->degree] != 0) {
        poly_int lead = old_r->coeffs[old_r->degree];
        poly_int lead_inv = mod_inverse(lead, p);
        Poly *monic_gcd = poly_scalar_mul(old_r, lead_inv, p);
        poly_free(old_r);
        old_r = monic_gcd;
        
        Poly *monic_s = poly_scalar_mul(old_s, lead_inv, p);
        poly_free(old_s);
        old_s = monic_s;
        
        Poly *monic_t = poly_scalar_mul(old_t, lead_inv, p);
        poly_free(old_t);
        old_t = monic_t;
    }

    if (x_out) *x_out = old_s; else poly_free(old_s);
    if (y_out) *y_out = old_t; else poly_free(old_t);

    return old_r;
}

Poly* poly_mod_inverse(const Poly *a, const Poly *m, poly_int p) {
    Poly *x = NULL;
    Poly *gcd = poly_ext_gcd(a, m, &x, NULL, p);
    poly_free(gcd); // Assume a and m are coprime, so gcd is 1
    return x;
}

// Fast polynomial exponentiation: base^exp % mod_poly over Z_p
Poly* poly_mod_pow(const Poly *base, poly_int exp, const Poly *mod_poly, poly_int p) {
    Poly *res = poly_create(0);
    res->coeffs[0] = 1;

    Poly *current_base = poly_copy(base);

    while (exp > 0) {
        if (exp % 2 == 1) {
            Poly *temp = poly_mul(res, current_base, p);
            Poly *temp_rem = poly_div_rem(temp, mod_poly, NULL, p);
            poly_free(res);
            poly_free(temp);
            res = temp_rem;
        }

        Poly *temp_base_sq = poly_mul(current_base, current_base, p);
        Poly *temp_base_rem = poly_div_rem(temp_base_sq, mod_poly, NULL, p);
        poly_free(current_base);
        poly_free(temp_base_sq);
        current_base = temp_base_rem;

        exp /= 2;
    }

    poly_free(current_base);
    return res;
}

// Gaussian elimination over Z_{p^e}. 
// matrix is size rows x cols.
// We assume it's an augmented matrix where we want to solve Ax = b, so cols = rows + 1.
// mod is p^e, p is the prime.
int solve_linear_system(poly_int **matrix, int rows, int cols, poly_int mod, poly_int p, poly_int *solution) {
    int num_vars = cols - 1;
    for (int i = 0; i < num_vars; i++) {
        // Find pivot: must be coprime to p to be invertible
        int pivot_row = i;
        int found = 0;
        for (int r = i; r < rows; r++) {
            if (matrix[r][i] % p != 0) {
                pivot_row = r;
                found = 1;
                break;
            }
        }
        
        if (!found) {
            // Cannot find an invertible pivot (matrix is singular over Z_p)
            return 0;
        }
        
        // Swap rows
        if (pivot_row != i) {
            for (int j = i; j < cols; j++) {
                poly_int temp = matrix[i][j];
                matrix[i][j] = matrix[pivot_row][j];
                matrix[pivot_row][j] = temp;
            }
        }
        
        // Normalize pivot row
        poly_int pivot_val = mod_val(matrix[i][i], mod);
        poly_int pivot_inv = mod_inverse(pivot_val, mod);
        for (int j = i; j < cols; j++) {
            matrix[i][j] = mod_val(matrix[i][j] * pivot_inv, mod);
        }
        
        // Eliminate below and above
        for (int r = 0; r < rows; r++) {
            if (r != i) {
                poly_int factor = matrix[r][i];
                for (int j = i; j < cols; j++) {
                    poly_int sub = mod_val(factor * matrix[i][j], mod);
                    matrix[r][j] = mod_val(matrix[r][j] - sub, mod);
                }
            }
        }
    }
    
    // Extract solution
    if (solution) {
        for (int i = 0; i < num_vars; i++) {
            solution[i] = matrix[i][cols - 1];
        }
    }
    return 1;
}

void poly_print(const Poly *p) {
    if (p->degree == 0 && p->coeffs[0] == 0) {
        printf("0");
        return;
    }
    int first = 1;
    for (int i = p->degree; i >= 0; i--) {
        if (p->coeffs[i] == 0) continue;
        if (!first && p->coeffs[i] > 0) printf(" + ");
        if (p->coeffs[i] < 0) printf(" - ");
        
        long long abs_c = p->coeffs[i] >= 0 ? p->coeffs[i] : -p->coeffs[i];
        if (abs_c != 1 || i == 0) printf("%lld", abs_c);
        
        if (i > 0) printf("x");
        if (i > 1) printf("^%d", i);
        first = 0;
    }
}
