#ifndef DICKSON_V3_H
#define DICKSON_V3_H

#include "poly_alg.h"
#include "dickson.h"

// Dickson Engine V3 — Universal Cyclotomic Factorizer
// Handles both unramified (gcd(n,p)=1) and ramified (p|n) regimes.

typedef struct {
    poly_int p;
    int e;
    poly_int final_mod;  // p^e
} DicksonEngineV3;

// Factor descriptor: one irreducible factor of X^n - 1 over Z_{p^e}
typedef struct {
    Poly *poly;          // The irreducible polynomial
    int coset_size;      // Degree (cyclotomic coset dimension)
    int ramification;    // Which ramification layer (0 = unramified)
} Factor;

// Factor list
typedef struct {
    Factor *factors;
    int count;
    int capacity;
} FactorList;

// --- V3 API ---

DicksonEngineV3* dickson_v3_init(poly_int p, int e);
void dickson_v3_free(DicksonEngineV3 *engine);

// The single entry point: fully factor X^n - 1 over Z_{p^e}
FactorList* dickson_v3_factor(DicksonEngineV3 *engine, poly_int n);

// Factor list management
FactorList* factor_list_create(int initial_capacity);
void factor_list_add(FactorList *list, Poly *poly, int coset_size, int ramification);
void factor_list_free(FactorList *list);
void factor_list_print(FactorList *list, poly_int mod);

// Verification: multiply all factors and check against X^n - 1 mod p^e
int dickson_v3_verify(FactorList *list, poly_int n, poly_int mod);

#endif // DICKSON_V3_H
