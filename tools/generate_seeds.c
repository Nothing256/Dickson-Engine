#include "../core/include/dickson_v2.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Specific list of benchmark primes observed in the tests + some low primes
poly_int benchmark_primes[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 199, 1009, 30011};
int num_primes = sizeof(benchmark_primes) / sizeof(poly_int);

int main(int argc, char** argv) {
    srand(time(NULL));
    
    printf("--- Dickson Engine V2 Seed Foundry ---\n");
    printf("Starting systematic seed search on benchmark primes...\n");

    FILE *out = fopen("core/src/primes_seeds.c", "w");
    if (!out) {
        printf("Error: Could not open core/src/primes_seeds.c for writing.\n");
        return 1;
    }

    fprintf(out, "// Auto-Generated Dickson V2 Seed Dictionary\n");
    fprintf(out, "// DO NOT EDIT MANUALLY\n\n");
    fprintf(out, "#include \"../include/primes_seeds.h\"\n");
    fprintf(out, "#include <stdlib.h>\n\n");

    fprintf(out, "Poly* get_precomputed_seed(poly_int p, int m) {\n");
    fprintf(out, "    Poly *seed = NULL;\n");

    for (int i = 0; i < num_primes; i++) {
        poly_int p = benchmark_primes[i];
        
        fprintf(out, "    if (p == %lld) {\n", p);

        // m = 2
        poly_int n2 = p + 1;
        DicksonEngineV2 *engine2 = dickson_v2_init(p, 1, 2);
        Poly *seed2 = dickson_v2_find_primitive_seed(engine2, n2);
        
        if (seed2) {
            fprintf(out, "        if (m == 2) {\n");
            fprintf(out, "            seed = poly_create(2);\n");
            for (int j = 0; j <= 2; j++) {
                fprintf(out, "            seed->coeffs[%d] = %lld;\n", j, seed2->coeffs[j]);
            }
            fprintf(out, "        }\n");
            poly_free(seed2);
        }
        dickson_v2_free(engine2);

        // m = 3
        poly_int n3 = p * p + p + 1;
        DicksonEngineV2 *engine3 = dickson_v2_init(p, 1, 3);
        Poly *seed3 = dickson_v2_find_primitive_seed(engine3, n3);
        
        if (seed3) {
            fprintf(out, "        if (m == 3) {\n");
            fprintf(out, "            seed = poly_create(3);\n");
            for (int j = 0; j <= 3; j++) {
                fprintf(out, "            seed->coeffs[%d] = %lld;\n", j, seed3->coeffs[j]);
            }
            fprintf(out, "        }\n");
            poly_free(seed3);
        }
        dickson_v2_free(engine3);

        fprintf(out, "    }\n");
    }

    fprintf(out, "    return seed;\n");
    fprintf(out, "}\n");

    fclose(out);
    
    printf("Foundry completed successfully! Wrote seeds array to core/src/primes_seeds.c\n");

    return 0;
}
