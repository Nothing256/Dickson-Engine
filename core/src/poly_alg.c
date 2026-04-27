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
    
    while (R->degree >= B->degree) {
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
