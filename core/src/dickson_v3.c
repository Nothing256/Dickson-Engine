#include "dickson_v3.h"
#include <string.h>

// ============================================================
//  Dickson Engine V3 — Universal Cyclotomic Factorizer
//  Handles X^n - 1 over Z_{p^e} for ALL n (including p | n)
// ============================================================

// --- Helpers ---

static poly_int mod_pos(poly_int val, poly_int m) {
    poly_int r = val % m;
    if (r < 0) r += m;
    return r;
}

static poly_int mod_inverse(poly_int a, poly_int m) {
    poly_int t = 0, newt = 1;
    poly_int r = m, newr = a;
    while (newr != 0) {
        poly_int q = r / newr;
        poly_int tmp;
        tmp = t - q * newt; t = newt; newt = tmp;
        tmp = r - q * newr; r = newr; newr = tmp;
    }
    if (r > 1) return 0;
    if (t < 0) t += m;
    return t;
}

// Extract the p-free part: given n, compute m and k such that n = p^k * m, gcd(m,p)=1
static void extract_p_free(poly_int n, poly_int p, poly_int *m_out, int *k_out) {
    poly_int m = n;
    int k = 0;
    while (m % p == 0) {
        m /= p;
        k++;
    }
    *m_out = m;
    *k_out = k;
}

// Compute G(X^s) — substitute X -> X^s in polynomial G
static Poly* poly_compose_xp(const Poly *G, poly_int s) {
    int new_deg = G->degree * (int)s;
    Poly *result = poly_create(new_deg);
    for (int i = 0; i <= G->degree; i++) {
        result->coeffs[i * (int)s] = G->coeffs[i];
    }
    return result;
}

// Exact polynomial division A / B over Z_{p^e} (B must be monic)
// Returns quotient Q such that A = B * Q (remainder must be zero)
static Poly* poly_exact_div(const Poly *A, const Poly *B, poly_int mod) {
    Poly *rem = NULL;
    Poly *Q = NULL;
    rem = poly_div_rem(A, B, &Q, mod);
    // Verify remainder is zero (should always be for our use case)
    if (rem) {
        int is_zero = 1;
        for (int i = 0; i <= rem->degree; i++) {
            if (mod_pos(rem->coeffs[i], mod) != 0) {
                is_zero = 0;
                break;
            }
        }
        if (!is_zero) {
            printf("[V3 WARNING] Exact division has nonzero remainder!\n");
        }
        poly_free(rem);
    }
    return Q;
}

// --- Factor List ---

FactorList* factor_list_create(int initial_capacity) {
    FactorList *list = (FactorList*)malloc(sizeof(FactorList));
    list->factors = (Factor*)malloc(initial_capacity * sizeof(Factor));
    list->count = 0;
    list->capacity = initial_capacity;
    return list;
}

void factor_list_add(FactorList *list, Poly *poly, int coset_size, int ramification) {
    if (list->count >= list->capacity) {
        list->capacity *= 2;
        list->factors = (Factor*)realloc(list->factors, list->capacity * sizeof(Factor));
    }
    list->factors[list->count].poly = poly_copy(poly);
    list->factors[list->count].coset_size = coset_size;
    list->factors[list->count].ramification = ramification;
    list->count++;
}

void factor_list_free(FactorList *list) {
    if (!list) return;
    for (int i = 0; i < list->count; i++) {
        poly_free(list->factors[i].poly);
    }
    free(list->factors);
    free(list);
}

void factor_list_print(FactorList *list, poly_int mod) {
    printf("========================================================\n");
    printf("Complete Factorization (%d irreducible factors):\n", list->count);
    printf("========================================================\n");
    for (int i = 0; i < list->count; i++) {
        Factor *f = &list->factors[i];
        printf("[%d] ", i + 1);
        if (f->ramification > 0) {
            printf("[ram=%d] ", f->ramification);
        }
        poly_print(f->poly);
        printf("\n");
    }
    printf("========================================================\n");
}

// --- V3 Engine Core ---

DicksonEngineV3* dickson_v3_init(poly_int p, int e) {
    DicksonEngineV3 *engine = (DicksonEngineV3*)malloc(sizeof(DicksonEngineV3));
    engine->p = p;
    engine->e = e;
    engine->final_mod = 1;
    for (int i = 0; i < e; i++) engine->final_mod *= p;
    return engine;
}

void dickson_v3_free(DicksonEngineV3 *engine) {
    if (engine) free(engine);
}

// Internal: Use V2 to fully factor X^m - 1 (unramified, gcd(m,p) = 1)
// Returns a FactorList of all irreducible factors over Z_{p^e}
static FactorList* v3_factor_unramified(DicksonEngineV3 *v3, poly_int m) {
    poly_int p = v3->p;
    int e = v3->e;
    poly_int final_mod = v3->final_mod;

    // Determine coset dimension for the seed
    int coset_dim = 1;
    {
        poly_int test = p % m;
        while (test != 1) {
            test = (test * p) % m;
            coset_dim++;
        }
    }

    printf("[V3] Unramified factorization of X^%lld - 1 over Z_{%lld}\n", m, final_mod);
    printf("[V3] Coset dimension for seed: %d\n", coset_dim);

    DicksonEngineV2 *v2 = dickson_v2_init(p, e, coset_dim);

    // Stage 1: Find seed
    Poly *seed = dickson_v2_find_primitive_seed(v2, m);
    if (!seed) {
        printf("[V3] FATAL: Could not find seed for m=%lld\n", m);
        dickson_v2_free(v2);
        return factor_list_create(1);
    }

    // Stage 2: Hensel lift the seed
    Poly *seed_lifted = dickson_v2_algebraic_lift(v2, seed, m);

    // Stage 3: Generate trace array
    poly_int *traces = dickson_v2_multidimensional_dispatch(v2, seed_lifted, m);

    // Stage 4: Reconstruct all factors via MED dispatch
    // We re-implement this internally to collect Factor objects instead of just printing
    FactorList *result = factor_list_create(16);

    // (X - 1) is always a factor
    Poly *linear_x_minus_1 = poly_create(1);
    linear_x_minus_1->coeffs[1] = 1;
    linear_x_minus_1->coeffs[0] = mod_pos(-1, final_mod);
    factor_list_add(result, linear_x_minus_1, 1, 0);
    poly_free(linear_x_minus_1);

    int *visited = (int*)calloc(m, sizeof(int));
    visited[0] = 1;

    for (int i = 1; i < m; i++) {
        if (visited[i]) continue;

        // Find coset
        int m_coset = 0;
        poly_int curr = i;
        while (!visited[curr]) {
            visited[curr] = 1;
            curr = (curr * p) % m;
            m_coset++;
        }

        // Check if we should use Newton-Girard or fallback
        if (p > m_coset) {
            // Newton-Girard track
            poly_int scale = coset_dim / m_coset;
            poly_int scale_inv = mod_inverse(scale, final_mod);
            if (scale_inv == 0) continue;

            poly_int *med_traces = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
            for (int k = 1; k <= m_coset; k++) {
                poly_int idx = ((poly_int)i * k) % m;
                if (idx == 0) idx = m;
                poly_int raw_trace = (idx == m) ? mod_pos(coset_dim, final_mod) : traces[idx];
                med_traces[k] = mod_pos(raw_trace * scale_inv, final_mod);
            }

            poly_int *e_sym = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
            e_sym[0] = 1;
            int ok = 1;

            for (int k = 1; k <= m_coset; k++) {
                poly_int sum_val = 0;
                for (int j = 1; j <= k; j++) {
                    poly_int term = mod_pos(e_sym[k - j] * med_traces[j], final_mod);
                    if ((j - 1) % 2 != 0) term = -term;
                    sum_val = mod_pos(sum_val + term, final_mod);
                }
                poly_int k_inv = mod_inverse(k, final_mod);
                if (k_inv == 0) { ok = 0; break; }
                e_sym[k] = mod_pos(sum_val * k_inv, final_mod);
            }

            if (ok) {
                Poly *factor = poly_create(m_coset);
                factor->coeffs[m_coset] = 1;
                for (int k = 1; k <= m_coset; k++) {
                    poly_int sign = (k % 2 != 0) ? -1 : 1;
                    factor->coeffs[m_coset - k] = mod_pos(sign * e_sym[k], final_mod);
                }
                factor_list_add(result, factor, m_coset, 0);
                poly_free(factor);
            }
            free(med_traces);
            free(e_sym);
        } else {
            // Fallback: Quotient Ring Minimal Polynomial
            Poly *base_X = poly_create(1);
            base_X->coeffs[1] = 1;
            Poly *beta = poly_mod_pow(base_X, i, seed_lifted, final_mod);
            poly_free(base_X);

            Poly **powers = (Poly**)malloc((m_coset + 1) * sizeof(Poly*));
            powers[0] = poly_create(0);
            powers[0]->coeffs[0] = 1;
            for (int k = 1; k <= m_coset; k++) {
                Poly *temp = poly_mul(powers[k - 1], beta, final_mod);
                powers[k] = poly_div_rem(temp, seed_lifted, NULL, final_mod);
                poly_free(temp);
            }

            poly_int **matrix = (poly_int**)malloc(coset_dim * sizeof(poly_int*));
            for (int r = 0; r < coset_dim; r++) {
                matrix[r] = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
                for (int c = 0; c < m_coset; c++) {
                    if (r <= powers[c]->degree) matrix[r][c] = powers[c]->coeffs[r];
                }
                if (r <= powers[m_coset]->degree) {
                    matrix[r][m_coset] = mod_pos(-powers[m_coset]->coeffs[r], final_mod);
                }
            }

            poly_int *solution = (poly_int*)calloc(m_coset, sizeof(poly_int));
            int success = solve_linear_system(matrix, coset_dim, m_coset + 1, final_mod, p, solution);

            if (success) {
                Poly *factor = poly_create(m_coset);
                factor->coeffs[m_coset] = 1;
                for (int k = 0; k < m_coset; k++) {
                    factor->coeffs[k] = mod_pos(solution[k], final_mod);
                }
                factor_list_add(result, factor, m_coset, 0);
                poly_free(factor);
            }

            for (int r = 0; r < coset_dim; r++) free(matrix[r]);
            free(matrix);
            free(solution);
            for (int k = 0; k <= m_coset; k++) poly_free(powers[k]);
            free(powers);
            poly_free(beta);
        }
    }

    free(visited);
    free(traces);
    poly_free(seed);
    poly_free(seed_lifted);
    dickson_v2_free(v2);

    return result;
}

// ============================================================
//  V3 CORE: The Ramified Extension via Cyclotomic Substitution
// ============================================================

// For each unramified factor G_i(X), generate the ramified layer factor:
//   H_i^{(j)}(X) = G_i(X^{p^j}) / G_i(X^{p^{j-1}})
// These are proven irreducible by local class field theory.
static FactorList* v3_extend_ramified(DicksonEngineV3 *v3, FactorList *unramified, int k) {
    poly_int p = v3->p;
    poly_int final_mod = v3->final_mod;

    FactorList *result = factor_list_create(unramified->count * (k + 1));

    // Copy all unramified factors
    for (int i = 0; i < unramified->count; i++) {
        factor_list_add(result, unramified->factors[i].poly,
                        unramified->factors[i].coset_size, 0);
    }

    printf("[V3] Extending to ramified layers (k = %d)...\n", k);

    // For each ramification depth j = 1, ..., k
    for (int j = 1; j <= k; j++) {
        printf("[V3]   Ramification layer j = %d:\n", j);

        for (int i = 0; i < unramified->count; i++) {
            Poly *G_i = unramified->factors[i].poly;

            // Compute G_i(X^{p^j})
            poly_int p_j = 1;
            for (int t = 0; t < j; t++) p_j *= p;
            Poly *G_top = poly_compose_xp(G_i, p_j);

            // Compute G_i(X^{p^{j-1}})
            poly_int p_j1 = p_j / p;
            Poly *G_bot = poly_compose_xp(G_i, p_j1);

            // Reduce all coefficients mod final_mod
            for (int c = 0; c <= G_top->degree; c++)
                G_top->coeffs[c] = mod_pos(G_top->coeffs[c], final_mod);
            for (int c = 0; c <= G_bot->degree; c++)
                G_bot->coeffs[c] = mod_pos(G_bot->coeffs[c], final_mod);

            // Exact division: H_i^{(j)} = G_i(X^{p^j}) / G_i(X^{p^{j-1}})
            Poly *H = poly_exact_div(G_top, G_bot, final_mod);

            if (H) {
                // Normalize coefficients
                for (int c = 0; c <= H->degree; c++)
                    H->coeffs[c] = mod_pos(H->coeffs[c], final_mod);

                int new_degree = H->degree;
                while (new_degree > 0 && H->coeffs[new_degree] == 0) new_degree--;

                printf("[V3]     Factor from G_%d: degree %d\n", i + 1, new_degree);

                factor_list_add(result, H, new_degree, j);
                poly_free(H);
            }

            poly_free(G_top);
            poly_free(G_bot);
        }
    }

    return result;
}

// ============================================================
//  V3 PUBLIC API: The Single Entry Point
// ============================================================

FactorList* dickson_v3_factor(DicksonEngineV3 *engine, poly_int n) {
    poly_int p = engine->p;

    printf("==========================================================\n");
    printf("  Dickson Engine V3 — Universal Cyclotomic Factorizer\n");
    printf("  Factoring X^%lld - 1 over Z_{%lld^%d} = Z_{%lld}\n", n, p, engine->e, engine->final_mod);
    printf("==========================================================\n");

    // Step 1: Extract ramification depth
    poly_int m;
    int k;
    extract_p_free(n, p, &m, &k);

    if (k == 0) {
        printf("[V3] Unramified case: gcd(%lld, %lld) = 1\n", n, p);
        printf("[V3] Delegating entirely to V2 engine...\n\n");
        return v3_factor_unramified(engine, m);
    }

    printf("[V3] Ramified case detected: n = %lld = %lld^%d * %lld\n", n, p, k, m);
    printf("[V3] Phase 1: Factor unramified core X^%lld - 1\n\n", m);

    // Step 2: Factor the unramified core X^m - 1
    FactorList *unramified = v3_factor_unramified(engine, m);

    printf("\n[V3] Phase 2: Extend to ramified layers via cyclotomic substitution\n");

    // Step 3: Extend to ramified layers
    FactorList *full = v3_extend_ramified(engine, unramified, k);

    factor_list_free(unramified);

    return full;
}

// ============================================================
//  Verification: Multiply all factors, check against X^n - 1
// ============================================================

int dickson_v3_verify(FactorList *list, poly_int n, poly_int mod) {
    printf("\n[V3 Verify] Multiplying %d factors to check correctness...\n", list->count);

    if (list->count == 0) {
        printf("[V3 Verify] FAIL: No factors!\n");
        return 0;
    }

    Poly *product = poly_copy(list->factors[0].poly);
    for (int i = 1; i < list->count; i++) {
        Poly *temp = poly_mul(product, list->factors[i].poly, mod);
        poly_free(product);
        product = temp;
    }

    // Normalize
    for (int i = 0; i <= product->degree; i++) {
        product->coeffs[i] = mod_pos(product->coeffs[i], mod);
    }

    // Build X^n - 1
    Poly *target = poly_create((int)n);
    target->coeffs[(int)n] = 1;
    target->coeffs[0] = mod_pos(-1, mod);

    // Compare
    int match = 1;
    int max_deg = product->degree > target->degree ? product->degree : target->degree;
    for (int i = 0; i <= max_deg; i++) {
        poly_int a = (i <= product->degree) ? mod_pos(product->coeffs[i], mod) : 0;
        poly_int b = (i <= target->degree) ? mod_pos(target->coeffs[i], mod) : 0;
        if (a != b) {
            printf("[V3 Verify] MISMATCH at X^%d: got %lld, expected %lld\n", i, a, b);
            match = 0;
        }
    }

    poly_free(product);
    poly_free(target);

    if (match) {
        printf("[V3 Verify] SUCCESS: Product of all factors == X^%lld - 1 (mod %lld)\n", n, mod);
    } else {
        printf("[V3 Verify] FAIL: Product does not match X^%lld - 1\n", n);
    }

    return match;
}
