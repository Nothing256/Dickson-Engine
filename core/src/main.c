#include "dickson.h"

int main() {
    printf("==================================================\n");
    printf("   Dickson Engine v2.0 - Multidimensional Array   \n");
    printf("==================================================\n");

    // Setting up parameters for the d=3 Subspace Rupture at n=p^2+p+1
    // p = 2, m = 3
    poly_int p = 2;
    int e = 3;
    int m = 3; 
    
    DicksonEngineV2 *engine = dickson_v2_init(p, e, m);

    // Initializing the base seed polynomial G_base(X) = X^3 - AX^2 + BX - 1 over F_2
    // We already know from our algebraic discovery that (A, B) = (0, 1) is a valid root trace!
    // So G_base(X) = X^3 - 0*X^2 + 1*X - 1 = X^3 + X - 1
    Poly *g_base = poly_create(3);
    g_base->coeffs[3] = 1; // X^3
    g_base->coeffs[2] = 0; // 0*X^2
    g_base->coeffs[1] = 1; // X
    g_base->coeffs[0] = -1; // -1
    
    // Stage 1 & 2: Local Seed Evaluation natively extracting remainders
    poly_int n = 14; // Need to supply n for testing
    Poly *g_lifted = dickson_v2_algebraic_lift(engine, g_base, n);

    // Stage 3: The True Multi-dimensional Space Propagator
    // We compute the first 10 traces dynamically from the base parameter symmetric combinations!
    dickson_v2_multidimensional_dispatch(engine, g_lifted, 10);

    // Cleanup
    poly_free(g_base);
    poly_free(g_lifted);
    dickson_v2_free(engine);

    printf("==================================================\n");
    return 0;
}
