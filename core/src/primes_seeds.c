// Auto-Generated Dickson V2 Seed Dictionary
// DO NOT EDIT MANUALLY

#include "../include/primes_seeds.h"
#include <stdlib.h>

Poly* get_precomputed_seed(poly_int p, int m) {
    Poly *seed = NULL;
    if (p == 2) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 1;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 1;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 3) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 2;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 1;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 5) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 4;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 4;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 7) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 6;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 6;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 11) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 5;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 10;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 6;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 13) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 10;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 12;
            seed->coeffs[1] = 9;
            seed->coeffs[2] = 8;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 17) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 14;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 16;
            seed->coeffs[1] = 9;
            seed->coeffs[2] = 0;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 19) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 11;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 18;
            seed->coeffs[1] = 5;
            seed->coeffs[2] = 17;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 23) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 8;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 22;
            seed->coeffs[1] = 19;
            seed->coeffs[2] = 22;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 29) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 28;
            seed->coeffs[1] = 13;
            seed->coeffs[2] = 19;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 31) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 20;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 30;
            seed->coeffs[1] = 14;
            seed->coeffs[2] = 2;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 199) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 162;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 198;
            seed->coeffs[1] = 33;
            seed->coeffs[2] = 20;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 1009) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 925;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 1008;
            seed->coeffs[1] = 1002;
            seed->coeffs[2] = 489;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 30011) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 22571;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 30010;
            seed->coeffs[1] = 17796;
            seed->coeffs[2] = 2789;
            seed->coeffs[3] = 1;
        }
    }
    return seed;
}
