#include "dickson_v3.h"
#include <time.h>

int main() {
    srand((unsigned)time(NULL));

    printf("╔══════════════════════════════════════════════════════╗\n");
    printf("║   Dickson Engine V3 — Universal Cyclotomic Factorizer  ║\n");
    printf("╚══════════════════════════════════════════════════════╝\n\n");

    // ============================================================
    // Test 1: Unramified case (should delegate to V2 seamlessly)
    // p=2, n=7, e=3 => gcd(7,2)=1, purely unramified
    // ============================================================
    {
        printf("━━━━━━━━━ TEST 1: Unramified p=2, n=7, e=3 ━━━━━━━━━\n\n");
        DicksonEngineV3 *engine = dickson_v3_init(2, 3);
        FactorList *factors = dickson_v3_factor(engine, 7);
        factor_list_print(factors, engine->final_mod);
        dickson_v3_verify(factors, 7, engine->final_mod);
        factor_list_free(factors);
        dickson_v3_free(engine);
        printf("\n\n");
    }

    // ============================================================
    // Test 2: Ramified case p=2, n=6, e=3
    // n = 6 = 2 * 3, so k=1, m=3
    // X^6-1 over Z_8 should have 4 irreducible factors:
    //   (X-1), (X+1), (X^2+X+1), (X^2+7X+1)
    // ============================================================
    {
        printf("━━━━━━━━━ TEST 2: Ramified p=2, n=6, e=3 ━━━━━━━━━\n\n");
        DicksonEngineV3 *engine = dickson_v3_init(2, 3);
        FactorList *factors = dickson_v3_factor(engine, 6);
        factor_list_print(factors, engine->final_mod);
        dickson_v3_verify(factors, 6, engine->final_mod);
        factor_list_free(factors);
        dickson_v3_free(engine);
        printf("\n\n");
    }

    // ============================================================
    // Test 3: Ramified case p=2, n=12, e=3
    // n = 12 = 2^2 * 3, so k=2, m=3
    // Two layers of ramification
    // ============================================================
    {
        printf("━━━━━━━━━ TEST 3: Ramified p=2, n=12, e=3 ━━━━━━━━━\n\n");
        DicksonEngineV3 *engine = dickson_v3_init(2, 3);
        FactorList *factors = dickson_v3_factor(engine, 12);
        factor_list_print(factors, engine->final_mod);
        dickson_v3_verify(factors, 12, engine->final_mod);
        factor_list_free(factors);
        dickson_v3_free(engine);
        printf("\n\n");
    }

    // ============================================================
    // Test 4: Ramified case p=3, n=12, e=2
    // n = 12 = 3 * 4, so k=1, m=4
    // X^12-1 over Z_9
    // ============================================================
    {
        printf("━━━━━━━━━ TEST 4: Ramified p=3, n=12, e=2 ━━━━━━━━━\n\n");
        DicksonEngineV3 *engine = dickson_v3_init(3, 2);
        FactorList *factors = dickson_v3_factor(engine, 12);
        factor_list_print(factors, engine->final_mod);
        dickson_v3_verify(factors, 12, engine->final_mod);
        factor_list_free(factors);
        dickson_v3_free(engine);
        printf("\n\n");
    }

    // ============================================================
    // Test 5: Ramified case p=5, n=20, e=2
    // n = 20 = 5 * 4, so k=1, m=4
    // X^20-1 over Z_25
    // ============================================================
    {
        printf("━━━━━━━━━ TEST 5: Ramified p=5, n=20, e=2 ━━━━━━━━━\n\n");
        DicksonEngineV3 *engine = dickson_v3_init(5, 2);
        FactorList *factors = dickson_v3_factor(engine, 20);
        factor_list_print(factors, engine->final_mod);
        dickson_v3_verify(factors, 20, engine->final_mod);
        factor_list_free(factors);
        dickson_v3_free(engine);
        printf("\n\n");
    }

    printf("╔══════════════════════════════════════════════════════╗\n");
    printf("║             All V3 Tests Complete!                     ║\n");
    printf("╚══════════════════════════════════════════════════════╝\n");

    return 0;
}
