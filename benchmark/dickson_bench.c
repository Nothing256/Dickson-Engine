#include "../core/include/dickson.h"
#include "../core/include/poly_alg.h"
#include "../core/include/primes_seeds.h"
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
    
    // Calculate m dynamically: it is exactly the size of the base MED cyclotomic coset
    // i.e., the multiplicative order of p modulo n
    int m = 1;
    poly_int curr = p % n;
    while (curr != 1 && m < n) {
        curr = (curr * (p % n)) % n;
        m++;
    }
    
    DicksonEngineV2 *engine = dickson_v2_init(p, e, m);
    
    int use_random = 0;
    for (int i = 4; i < argc; i++) {
        if (strcmp(argv[i], "--random") == 0) {
            use_random = 1;
        }
    }
    
    double start = get_time();
    Poly *seed = NULL;
    if (!use_random) {
        seed = get_precomputed_seed(p, m);
        if (!seed) {
            printf("Error: No precomputed seed found for p=%lld. Use --random to auto-seed.\n", p);
            dickson_v2_free(engine);
            return 1;
        }
    } else {
        seed = dickson_v2_find_primitive_seed(engine, n);
    }
    if (seed) {
        double t1 = get_time();
        Poly *lifted = dickson_v2_algebraic_lift(engine, seed, n);
        double t2 = get_time();
        printf("Time algebraic_lift: %.6f\n", t2 - t1);
        
        poly_int *T = dickson_v2_multidimensional_dispatch(engine, lifted, n);
        double t3 = get_time();
        printf("Time multidimensional_dispatch: %.6f\n", t3 - t2);
        
        // --- Full Factorization Reconstruction ---
        // dickson_v2_reconstruct_factors(engine, T, n, lifted);
        
        free(T);
        poly_free(lifted);
        poly_free(seed);
    }
    double end = get_time();
    
    printf("Time Elapsed : %.6f\n", end - start);
    
    dickson_v2_free(engine);
    return 0;
}
