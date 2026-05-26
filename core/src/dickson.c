#include "dickson.h"
#include <string.h>

DicksonEngineV2* dickson_v2_init(poly_int p, int e, int m) {
    DicksonEngineV2 *engine = (DicksonEngineV2*)malloc(sizeof(DicksonEngineV2));
    engine->p = p;
    engine->e = e;
    engine->m = m;
    engine->final_mod = p;
    for(int i = 1; i < e; i++) {
        engine->final_mod *= p;
    }
    return engine;
}

void dickson_v2_free(DicksonEngineV2 *engine) {
    if (engine) free(engine);
}

// Internal mod helper
static poly_int mod_pos(poly_int val, poly_int m) {
    poly_int r = val % m;
    if (r < 0) r += m;
    return r;
}

// Multidimensional Algebraic Lifter
// Uses remainder evaluation on Fp to lift coefficients strictly over Z_{p^e}
Poly* dickson_v2_algebraic_lift(DicksonEngineV2 *engine, Poly *G_base, poly_int n_val) {
    printf("[Dickson Engine v2] Initiating Jacobion-Free Algebraic Seed Lift...\n");
    printf("Base Polynomial in F_%lld: ", engine->p);
    poly_print(G_base);
    printf("\n");

    Poly *G_lifted = poly_copy(G_base);
    poly_int current_mod = engine->p;
    poly_int p = engine->p;

    if (engine->e <= 1) {
        printf("[Dickson Engine v2] Precision e=1, skipping algebraic lift.\n");
        return G_lifted;
    }

    // --- PRE-COMPUTATION (H_inv Caching) ---
    // Construct X^n - 1 to extract H_1(X) over F_p
    Poly *Xn_minus_1 = poly_create(n_val);
    Xn_minus_1->coeffs[n_val] = 1;
    Xn_minus_1->coeffs[0] = -1;

    Poly *H_1 = NULL;
    Poly *R_0 = poly_div_rem(Xn_minus_1, G_base, &H_1, p);
    poly_free(R_0); // R_0 should be 0 mod p, since G_base is a factor
    
    // Compute the universally reusable inverse H_inv(X) mod G_1(X) over F_p
    Poly *H_inv = poly_mod_inverse(H_1, G_base, p);
    poly_free(H_1);
    poly_free(Xn_minus_1);

    if (!H_inv) {
        printf("[Dickson Engine v2] FATAL: H_1(X) is not invertible mod G_1(X). Lift failed.\n");
        poly_free(G_lifted);
        return NULL;
    }

    // --- FAST LIFTING LOOP ---
    Poly *X_poly = poly_create(1);
    X_poly->coeffs[1] = 1;

    for (int h = 1; h < engine->e; h++) {
        poly_int next_mod = current_mod * p;
        // printf(" -> Lifting locally to Z_{p^%d} (mod %lld) using remainder mapping...\n", h+1, next_mod);
        
        // 1. Fast Remainder: X^n - 1 mod G_h(X) over Z_{p^{h+1}}
        Poly *Xn_mod = poly_mod_pow(X_poly, n_val, G_lifted, next_mod);
        Poly *R_h = poly_copy(Xn_mod);
        R_h->coeffs[0] = mod_pos(R_h->coeffs[0] - 1, next_mod);
        poly_free(Xn_mod);
        
        // 2. Extract E(X) = R_h(X) / p^h mod p
        Poly *E = poly_create(R_h->degree);
        for (int i = 0; i <= R_h->degree; i++) {
            poly_int raw_val = R_h->coeffs[i];
            if (raw_val < 0) raw_val += next_mod;
            
            // Should be completely divisible by current_mod (p^h)
            poly_int e_val = (raw_val / current_mod) % p;
            E->coeffs[i] = mod_pos(e_val, p);
        }
        
        // 3. Compute Delta G(X) = E(X) * H_inv(X) mod G_1(X) over F_p
        // Notice we REUSE the cached H_inv here!
        Poly *E_mul_Hinv = poly_mul(E, H_inv, p);
        Poly *Delta_G = poly_div_rem(E_mul_Hinv, G_base, NULL, p);
        
        // 4. Construct G_{h+1}(X) = G_h(X) + p^h * Delta_G(X) mod p^{h+1}
        for (int i = 0; i <= Delta_G->degree && i <= G_lifted->degree; i++) {
            poly_int delta_val = mod_pos(Delta_G->coeffs[i], p);
            poly_int scaled_delta = mod_pos(delta_val * current_mod, next_mod);
            G_lifted->coeffs[i] = mod_pos(G_lifted->coeffs[i] + scaled_delta, next_mod);
        }
        
        poly_free(R_h);
        poly_free(E);
        poly_free(E_mul_Hinv);
        poly_free(Delta_G);
        
        current_mod = next_mod;
    }

    poly_free(X_poly);
    poly_free(H_inv);

    printf("[Dickson Engine v2] Completed Homogeneous Algebraic Lift.\n");
    printf("Lifted Polynomial in Z_%lld: ", current_mod);
    poly_print(G_lifted);
    printf("\n");
    
    return G_lifted;
}

// The Power of Multidimensional Dickson Recurrences (Generalized Girard loops)
poly_int* dickson_v2_multidimensional_dispatch(DicksonEngineV2 *engine, Poly *G_lifted, poly_int total_target_traces) {
    printf("[Dickson Engine v2] Deploying Multi-dimensional Dickson Generator Array...\n");
    // Standard Girard-Newton Traces extraction array:
    // T_k = sum_{j=1}^m (-1)^{j-1} c_j T_{k-j}
    // Note: G_lifted coefficients are X^m + c_{m-1} X^{m-1} + ... + c_0
    // We rewrite it structurally: X^m - A_1 X^{m-1} + A_2 X^{m-2} - ... 

    int m = engine->m;
    poly_int *A = (poly_int*)calloc(m + 1, sizeof(poly_int));
    for (int j = 1; j <= m; j++) {
        // A_j correlates to the coefficient of X^{m-j}
        poly_int coeff = G_lifted->coeffs[m - j];
        // Sign inversion logic to extract symmetric parameters A_j cleanly
        poly_int sign = (j % 2 != 0) ? -1 : 1; 
        A[j] = mod_pos(coeff * sign, engine->final_mod);
    }

    // Allocate trace array. Ensure it has at least 'm' elements to safely complete Newton initialization.
    int max_T = (total_target_traces > m) ? total_target_traces : m;
    poly_int *T = (poly_int*)calloc(max_T + 1, sizeof(poly_int));
    
    // Initial dynamic traces over Z_{p^e}
    T[0] = m;
    // T_1 = A_1
    if (total_target_traces >= 1) T[1] = A[1];
    
    for (int k = 2; k <= m; k++) {
        poly_int param_sum = 0;
        for (int j = 1; j < k; j++) {
            poly_int term = mod_pos(A[j] * T[k - j], engine->final_mod);
            poly_int sign = (j % 2 != 0) ? 1 : -1;
            param_sum = mod_pos(param_sum + sign * term, engine->final_mod);
        }
        poly_int tail = mod_pos(k * A[k], engine->final_mod);
        poly_int tail_sign = (k % 2 != 0) ? 1 : -1;
        T[k] = mod_pos(param_sum + tail_sign * tail, engine->final_mod);
    }

    // The true generalized independent multi-term generator (bypassing the simplistic 1D structure)
    for (int k = m + 1; k <= total_target_traces; k++) {
        poly_int next_T = 0;
        for (int j = 1; j <= m; j++) {
            poly_int term = mod_pos(A[j] * T[k - j], engine->final_mod);
            poly_int sign = (j % 2 != 0) ? 1 : -1;
            next_T = mod_pos(next_T + sign * term, engine->final_mod);
        }
        T[k] = next_T;
    }

    printf("Generated Generalized Multi-dimensional Seed Traces:\n");
    for (int k = 1; k <= total_target_traces; k++) {
        printf(" Trace T[%d] = %lld\n", k, T[k]);
    }

    free(A);
    return T;
}

// Internal inverse helper
static poly_int local_mod_inverse(poly_int a, poly_int m) {
    poly_int t = 0, newt = 1;
    poly_int r = m, newr = a;
    while (newr != 0) {
        poly_int quotient = r / newr;
        poly_int temp = t - quotient * newt;
        t = newt; newt = temp;
        temp = r - quotient * newr;
        r = newr; newr = temp;
    }
    if (r > 1) return 0;
    if (t < 0) t += m;
    return t;
}

// Fallback: Division-Free Multivariate Dickson Polynomial Generation using Quotient Ring Minimal Polynomials
static void fallback_multivariate_dickson_reconstruct(DicksonEngineV2 *engine, poly_int n, Poly *G_lifted) {
    printf(" [WARNING] Characteristic p=%lld <= m=%d. Newton-Girard is non-invertible.\n", engine->p, engine->m);
    printf("           Triggering Division-Free Multivariate Dickson Generation (Matrix-based)...\n");
    printf("========================================================\n\n");
    
    int factor_count = 0;
    int *visited = (int*)calloc(n, sizeof(int));
    poly_int p = engine->p;
    poly_int final_mod = engine->final_mod;
    int m = engine->m;
    
    // Add (x - 1)
    printf("[%d] (x - 1)\n", ++factor_count);
    visited[0] = 1;
    
    // Use the lifted seed polynomial
    Poly *seed = poly_copy(G_lifted);
    
    for (int i = 1; i < n; i++) {
        if (!visited[i]) {
            int m_coset = 0;
            poly_int curr = i;
            while (!visited[curr]) {
                visited[curr] = 1;
                curr = (curr * p) % n;
                m_coset++;
            }
            
            // We want the minimal polynomial of X^i mod seed(X)
            Poly *base_X = poly_create(1);
            base_X->coeffs[1] = 1;
            Poly *beta = poly_mod_pow(base_X, i, seed, final_mod);
            poly_free(base_X);
            
            // Compute powers: 1, beta, beta^2, ..., beta^{m_coset}
            Poly **powers = (Poly**)malloc((m_coset + 1) * sizeof(Poly*));
            powers[0] = poly_create(0);
            powers[0]->coeffs[0] = 1;
            for (int k = 1; k <= m_coset; k++) {
                Poly *temp = poly_mul(powers[k - 1], beta, final_mod);
                powers[k] = poly_div_rem(temp, seed, NULL, final_mod);
                poly_free(temp);
            }
            
            // Build linear system M * c = -powers[m_coset]
            // We expect the degree of relations to be bounded by m
            poly_int **matrix = (poly_int**)malloc(m * sizeof(poly_int*));
            for (int r = 0; r < m; r++) {
                matrix[r] = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
                for (int c = 0; c < m_coset; c++) {
                    if (r <= powers[c]->degree) matrix[r][c] = powers[c]->coeffs[r];
                }
                // Target column
                if (r <= powers[m_coset]->degree) {
                    matrix[r][m_coset] = mod_pos(-powers[m_coset]->coeffs[r], final_mod);
                }
            }
            
            poly_int *solution = (poly_int*)calloc(m_coset, sizeof(poly_int));
            int success = solve_linear_system(matrix, m, m_coset + 1, final_mod, p, solution);
            
            if (success) {
                printf("[%d] (x", ++factor_count);
                if (m_coset > 1) printf("^%d", m_coset);
                
                for (int k = 1; k <= m_coset; k++) {
                    poly_int final_coeff = solution[m_coset - k];
                    
                    if (final_coeff != 0) {
                        poly_int print_coeff = final_coeff;
                        if (print_coeff > final_mod / 2) print_coeff -= final_mod;
                        
                        if (print_coeff > 0) printf(" + ");
                        else if (print_coeff < 0) { printf(" - "); print_coeff = -print_coeff; }
                        
                        if (print_coeff != 1 || k == m_coset) printf("%lld", print_coeff);
                        
                        int power = m_coset - k;
                        if (power > 0) printf("x");
                        if (power > 1) printf("^%d", power);
                    }
                }
                printf(")\n");
            } else {
                printf("[%d] [Degenerate Coset] Matrix singularity in Multivariate Generation\n", ++factor_count);
            }
            
            // Cleanup
            for (int r = 0; r < m; r++) free(matrix[r]);
            free(matrix);
            free(solution);
            for (int k = 0; k <= m_coset; k++) poly_free(powers[k]);
            free(powers);
            poly_free(beta);
        }
    }
    
    poly_free(seed);
    free(visited);
    printf("Total Factors: %d\n", factor_count);
    printf("------------------------------------------\n");
}

// Full Factorization Reconstruction (MED Partitioning & Newton-Girard)
void dickson_v2_reconstruct_factors(DicksonEngineV2 *engine, poly_int *T, poly_int n, Poly *G_lifted) {
    printf("\n========================================================\n");
    printf("Full Factorization (Reconstructed via MED & Newton-Girard):\n");
    
    if (engine->p <= engine->m) {
        fallback_multivariate_dickson_reconstruct(engine, n, G_lifted);
        return;
    }
    
    int *visited = (int*)calloc(n, sizeof(int));
    int factor_count = 0;
    
    poly_int p = engine->p;
    poly_int final_mod = engine->final_mod;
    int m = engine->m;
    
    // Add (x - 1) which corresponds to root 1 (index 0)
    printf("[%d] (x - 1)\n", ++factor_count);
    visited[0] = 1;
    
    for (int i = 1; i < n; i++) {
        if (!visited[i]) {
            // Find coset size
            int m_coset = 0;
            poly_int curr = i;
            while (!visited[curr]) {
                visited[curr] = 1;
                curr = (curr * p) % n;
                m_coset++;
            }
            
            // Extract MED traces and scale
            poly_int scale = m / m_coset;
            poly_int scale_inv = local_mod_inverse(scale, final_mod);
            if (scale_inv == 0) {
                // If scale is not invertible, fallback (very rare unless p | scale)
                printf("[%d] [Degenerate Coset] Failed to invert scale factor\n", ++factor_count);
                continue;
            }
            
            poly_int *med_traces = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
            for (int k = 1; k <= m_coset; k++) {
                poly_int idx = (i * k) % n;
                if (idx == 0) idx = n;
                
                poly_int raw_trace = (idx == n) ? mod_pos(m, final_mod) : T[idx];
                med_traces[k] = mod_pos(raw_trace * scale_inv, final_mod);
            }
            
            // Newton-Girard
            poly_int *e_sym = (poly_int*)calloc(m_coset + 1, sizeof(poly_int));
            e_sym[0] = 1;
            
            int reconstruct_success = 1;
            for (int k = 1; k <= m_coset; k++) {
                poly_int sum_val = 0;
                for (int j = 1; j <= k; j++) {
                    poly_int term = mod_pos(e_sym[k - j] * med_traces[j], final_mod);
                    if ((j - 1) % 2 != 0) term = -term;
                    sum_val = mod_pos(sum_val + term, final_mod);
                }
                
                poly_int k_inv = local_mod_inverse(k, final_mod);
                if (k_inv == 0) {
                    reconstruct_success = 0;
                    break;
                }
                e_sym[k] = mod_pos(sum_val * k_inv, final_mod);
            }
            
            if (reconstruct_success) {
                printf("[%d] (x", ++factor_count);
                if (m_coset > 1) printf("^%d", m_coset);
                
                for (int k = 1; k <= m_coset; k++) {
                    poly_int coeff = e_sym[k];
                    poly_int sign = (k % 2 != 0) ? -1 : 1;
                    poly_int final_coeff = mod_pos(sign * coeff, final_mod);
                    
                    if (final_coeff != 0) {
                        poly_int print_coeff = final_coeff;
                        // Print negative numbers if they are shorter (e.g., -1 instead of p-1)
                        if (print_coeff > final_mod / 2) print_coeff -= final_mod;
                        
                        if (print_coeff > 0) printf(" + ");
                        else if (print_coeff < 0) { printf(" - "); print_coeff = -print_coeff; }
                        
                        if (print_coeff != 1 || k == m_coset) printf("%lld", print_coeff);
                        
                        int power = m_coset - k;
                        if (power > 0) printf("x");
                        if (power > 1) printf("^%d", power);
                    }
                }
                printf(")\n");
            } else {
                printf("[%d] [Degenerate Coset] Newton-Girard failed to invert k\n", ++factor_count);
            }
            
            free(med_traces);
            free(e_sym);
        }
    }
    
    printf("Total Factors: %d\n", factor_count);
    printf("------------------------------------------\n");
    free(visited);
}

// --- Dual-Mode Engine: Auto-Seeder ---

// Simple Trial Division to extract unique prime factors of n
static int get_prime_factors(poly_int n, poly_int *factors) {
    int count = 0;
    poly_int d = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            factors[count++] = d;
            while (n % d == 0) n /= d;
        }
        d++;
    }
    if (n > 1) {
        factors[count++] = n;
    }
    return count;
}

// Finds a primitive polynomial over F_p using rigorous Integrity Checks (O(log n))
Poly* dickson_v2_find_primitive_seed(DicksonEngineV2 *engine, poly_int n_val) {
    printf("[Auto-Seeder] Activating Dual-Mode Benchmark Engine...\n");
    printf("[Auto-Seeder] Target Dimension: %d, Order n: %lld. Initializing fast poly mod exponentiation...\n", engine->m, n_val);

    poly_int factors[64];
    int num_factors = get_prime_factors(n_val, factors);

    // Prepare X
    Poly *X = poly_create(1);
    X->coeffs[1] = 1;

    for (int attempt = 1; attempt <= 200000000; attempt++) {
        // 1. Generate Random Monic Polynomial G(X) of degree m
        // G(X) = X^m + c_{m-1}X^{m-1} ... + c_0
        Poly *G = poly_create(engine->m);
        G->coeffs[engine->m] = 1;
        // Constant term must be nonzero (irreducible poly cannot have 0 as root).
        // For general n, the norm of roots can be any nonzero element in GF(p),
        // so we randomize it instead of hardcoding (-1)^m (which only works for n=p+1).
        G->coeffs[0] = 1 + (rand() % (engine->p - 1));
        
        for (int i = 1; i < engine->m; i++) {
            G->coeffs[i] = rand() % engine->p;
        }

        // 2. Strict Integrity Check: X^n == 1 mod G(X)?
        Poly *res_n = poly_mod_pow(X, n_val, G, engine->p);
        int is_root = (res_n->degree == 0 && res_n->coeffs[0] == 1);
        poly_free(res_n);

        if (!is_root) {
            poly_free(G);
            continue; // Not a factor of X^n - 1
        }

        // 3. Short-Cycle Defense (Collision Check): X^{n/q} != 1 mod G(X)
        int is_primitive = 1;
        for (int i = 0; i < num_factors; i++) {
            poly_int sub_order = n_val / factors[i];
            Poly *res_sub = poly_mod_pow(X, sub_order, G, engine->p);
            
            if (res_sub->degree == 0 && res_sub->coeffs[0] == 1) {
                is_primitive = 0; // Short cycle detected!
                poly_free(res_sub);
                break;
            }
            poly_free(res_sub);
        }

        if (is_primitive) {
            printf("[Auto-Seeder] Success! Found rigorous Primitive Seed at attempt %d!\n", attempt);
            poly_free(X);
            return G;
        }

        poly_free(G);
    }
    
    poly_free(X);
    printf("[Auto-Seeder] WARNING: Exhausted attempts without finding a primitive seed.\n");
    return NULL;
}
