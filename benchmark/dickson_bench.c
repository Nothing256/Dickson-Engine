#include "../core/include/dickson.h"
#include "../core/include/poly_alg.h"
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>

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
    
    int m = 3; 
    
    DicksonEngineV2 *engine = dickson_v2_init(p, e, m);
    
    double start = get_time();
    Poly *seed = dickson_v2_find_primitive_seed(engine, n);
    if (seed) {
        Poly *lifted = dickson_v2_algebraic_lift(engine, seed);
        dickson_v2_multidimensional_dispatch(engine, lifted, 10);
        poly_free(lifted);
        poly_free(seed);
    }
    double end = get_time();
    
    printf("Time Elapsed : %.6f\n", end - start);
    
    dickson_v2_free(engine);
    return 0;
}
