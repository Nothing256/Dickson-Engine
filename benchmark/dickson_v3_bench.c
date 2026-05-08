/*
 * Dickson Engine V3 — Benchmark Binary
 *
 * Usage: dickson_v3_bench <p> <e> <n>
 *
 * Outputs:
 *   Factor Count : <count>
 *   Verified     : YES/NO
 *   Time Elapsed : <seconds>
 */

#include "../core/include/dickson_v3.h"
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

double get_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec * 1e-6;
}

int main(int argc, char** argv) {
    if (argc < 4) {
        printf("Usage: %s <p> <e> <n>\n", argv[0]);
        return 1;
    }
    poly_int p = atoll(argv[1]);
    int e = atoi(argv[2]);
    poly_int n = atoll(argv[3]);

    /* Suppress verbose output for benchmarking */
    int quiet = (argc >= 5 && strcmp(argv[4], "--quiet") == 0);

    srand(42);  /* Deterministic seed for reproducibility */

    DicksonEngineV3 *engine = dickson_v3_init(p, e);

    double start = get_time();
    FactorList *factors = dickson_v3_factor(engine, n);
    double end = get_time();

    int verified = dickson_v3_verify(factors, n, engine->final_mod);

    if (!quiet) {
        factor_list_print(factors, engine->final_mod);
    }

    printf("Factor Count : %d\n", factors->count);
    printf("Verified     : %s\n", verified ? "YES" : "NO");
    printf("Time Elapsed : %.6f\n", end - start);

    factor_list_free(factors);
    dickson_v3_free(engine);
    return 0;
}
