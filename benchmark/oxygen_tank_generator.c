#include "../core/include/dickson.h"
#include <stdio.h>
#include <stdlib.h>

int is_prime(poly_int p) {
    if (p < 2) return 0;
    if (p == 2 || p == 3) return 1;
    if (p % 2 == 0 || p % 3 == 0) return 0;
    for (poly_int i = 5; i * i <= p; i += 6) {
        if (p % i == 0 || p % (i + 2) == 0) return 0;
    }
    return 1;
}

int main() {
    FILE *fp = fopen("../core/src/primes_seeds.c", "w");
    if (!fp) {
        printf("Error: Could not open primes_seeds.c for writing.\n");
        return 1;
    }

    fprintf(fp, "// Auto-Generated Dickson V2 Seed Dictionary (Oxygen Tank)\n");
    fprintf(fp, "// Generated dynamically by Oxygen Tank Generator\n\n");
    fprintf(fp, "#include \"../include/primes_seeds.h\"\n");
    fprintf(fp, "#include <stdlib.h>\n\n");
    fprintf(fp, "Poly* get_precomputed_seed(poly_int p, int m) {\n");
    fprintf(fp, "    Poly *seed = NULL;\n");

    poly_int max_p = 200; // Adjust on Ubuntu for larger arsenal
    
    printf("Starting Oxygen Tank Generation up to p = %lld...\n", max_p);

    for (poly_int p = 2; p <= max_p; p++) {
        if (!is_prime(p)) continue;
        
        fprintf(fp, "    if (p == %lld) {\n", p);

        // For m = 2 (n = p + 1)
        poly_int n2 = p + 1;
        DicksonEngineV2 *engine2 = dickson_v2_init(p, 1, 2);
        Poly *seed2 = dickson_v2_find_primitive_seed(engine2, n2);
        if (seed2) {
            fprintf(fp, "        if (m == 2) {\n");
            fprintf(fp, "            seed = poly_create(2);\n");
            for (int i=0; i<=2; i++) {
                fprintf(fp, "            seed->coeffs[%d] = %lld;\n", i, seed2->coeffs[i]);
            }
            fprintf(fp, "        }\n");
            poly_free(seed2);
        }
        dickson_v2_free(engine2);

        // For m = 3 (n = p^2 + p + 1)
        poly_int n3 = p*p + p + 1;
        DicksonEngineV2 *engine3 = dickson_v2_init(p, 1, 3);
        Poly *seed3 = dickson_v2_find_primitive_seed(engine3, n3);
        if (seed3) {
            fprintf(fp, "        if (m == 3) {\n");
            fprintf(fp, "            seed = poly_create(3);\n");
            for (int i=0; i<=3; i++) {
                fprintf(fp, "            seed->coeffs[%d] = %lld;\n", i, seed3->coeffs[i]);
            }
            fprintf(fp, "        }\n");
            poly_free(seed3);
        }
        dickson_v2_free(engine3);

        fprintf(fp, "    }\n");
        printf("Generated precomputed seeds for p = %lld\n", p);
    }

    poly_int target_p = 30011;
    fprintf(fp, "    if (p == %lld) {\n", target_p);

    // For m = 2 (n = p + 1)
    poly_int n2_target = target_p + 1;
    DicksonEngineV2 *engine2_target = dickson_v2_init(target_p, 1, 2);
    Poly *seed2_target = dickson_v2_find_primitive_seed(engine2_target, n2_target);
    if (seed2_target) {
        fprintf(fp, "        if (m == 2) {\n");
        fprintf(fp, "            seed = poly_create(2);\n");
        for (int i=0; i<=2; i++) {
            fprintf(fp, "            seed->coeffs[%d] = %lld;\n", i, seed2_target->coeffs[i]);
        }
        fprintf(fp, "        }\n");
        poly_free(seed2_target);
    }
    dickson_v2_free(engine2_target);

    // For m = 3 (n = p^2 + p + 1)
    poly_int n3_target = target_p*target_p + target_p + 1;
    DicksonEngineV2 *engine3_target = dickson_v2_init(target_p, 1, 3);
    Poly *seed3_target = dickson_v2_find_primitive_seed(engine3_target, n3_target);
    if (seed3_target) {
        fprintf(fp, "        if (m == 3) {\n");
        fprintf(fp, "            seed = poly_create(3);\n");
        for (int i=0; i<=3; i++) {
            fprintf(fp, "            seed->coeffs[%d] = %lld;\n", i, seed3_target->coeffs[i]);
        }
        fprintf(fp, "        }\n");
        poly_free(seed3_target);
    }
    dickson_v2_free(engine3_target);

    fprintf(fp, "    }\n");
    printf("Generated precomputed seeds for p = %lld\n", target_p);

    fprintf(fp, "    return seed;\n");
    fprintf(fp, "}\n");
    fclose(fp);
    
    printf("Successfully wrote Oxygen Tank dictionary to core/src/primes_seeds.c.\n");
    printf("Remember to recompile (make) the project to link the new dictionary!\n");

    return 0;
}
