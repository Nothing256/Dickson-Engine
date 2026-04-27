#ifndef DICKSON_V2_H
#define DICKSON_V2_H

#include "poly_alg.h"

// Dickson Engine v2.0 - Multidimensional Algebraic Processor

typedef struct {
    poly_int p;
    int e;
    int m; // Expansion Dimension (e.g., m=3 for X^3 - AX^2 + BX - 1)
    poly_int final_mod; // p^e
} DicksonEngineV2;

DicksonEngineV2* dickson_v2_init(poly_int p, int e, int m);
void dickson_v2_free(DicksonEngineV2 *engine);

// Stage 2: Algebraic Seed Lifting (Jacobian-Free)
// We lift the irreducible base polynomial G(X) from mod p to mod p^e 
// using strictly polynomial arithmetic E(x) = Delta H(x) G(x) - Delta A X H(x).
// Note: This bypasses all multivariate Jacobians.
Poly* dickson_v2_algebraic_lift(DicksonEngineV2 *engine, Poly *G_base);

// Stage 3: Multi-dimensional Dickson Array Generation
// Instead of D_i = A D_{i-1} - D_{i-2}, we use the general m-term recurrence (Newton-Girard array).
void dickson_v2_multidimensional_dispatch(DicksonEngineV2 *engine, Poly *G_lifted, poly_int total_target_traces);

// --- Dual-Mode Engine: Auto-Seeder ---
// Finds a guaranteed primitive seed matrix/polynomial G(X) over F_p of degree m using strict Integrity Checks.
Poly* dickson_v2_find_primitive_seed(DicksonEngineV2 *engine, poly_int n_val);

#endif
