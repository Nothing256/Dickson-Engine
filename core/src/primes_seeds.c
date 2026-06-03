// Auto-Generated Dickson V2 Seed Dictionary (Oxygen Tank)
// Generated dynamically by Oxygen Tank Generator

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
            seed->coeffs[1] = 1;
            seed->coeffs[2] = 0;
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
            seed->coeffs[1] = 1;
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
            seed->coeffs[1] = 1;
            seed->coeffs[2] = 0;
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
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 0;
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
            seed->coeffs[1] = 9;
            seed->coeffs[2] = 5;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 13) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 7;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 12;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 7;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 17) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 7;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 16;
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 3;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 19) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 6;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 18;
            seed->coeffs[1] = 6;
            seed->coeffs[2] = 9;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 23) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 3;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 22;
            seed->coeffs[1] = 7;
            seed->coeffs[2] = 6;
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
            seed->coeffs[1] = 4;
            seed->coeffs[2] = 5;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 31) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 27;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 30;
            seed->coeffs[1] = 15;
            seed->coeffs[2] = 25;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 37) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 19;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 36;
            seed->coeffs[1] = 2;
            seed->coeffs[2] = 33;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 41) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 8;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 40;
            seed->coeffs[1] = 15;
            seed->coeffs[2] = 8;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 43) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 16;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 42;
            seed->coeffs[1] = 40;
            seed->coeffs[2] = 5;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 47) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 27;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 46;
            seed->coeffs[1] = 38;
            seed->coeffs[2] = 17;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 53) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 7;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 52;
            seed->coeffs[1] = 29;
            seed->coeffs[2] = 40;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 59) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 30;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 58;
            seed->coeffs[1] = 33;
            seed->coeffs[2] = 42;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 61) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 56;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 60;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 42;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 67) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 51;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 66;
            seed->coeffs[1] = 47;
            seed->coeffs[2] = 53;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 71) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 31;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 70;
            seed->coeffs[1] = 13;
            seed->coeffs[2] = 26;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 73) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 22;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 72;
            seed->coeffs[1] = 0;
            seed->coeffs[2] = 22;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 79) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 64;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 78;
            seed->coeffs[1] = 56;
            seed->coeffs[2] = 3;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 83) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 6;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 82;
            seed->coeffs[1] = 9;
            seed->coeffs[2] = 34;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 89) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 78;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 88;
            seed->coeffs[1] = 82;
            seed->coeffs[2] = 15;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 97) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 9;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 96;
            seed->coeffs[1] = 93;
            seed->coeffs[2] = 30;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 101) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 43;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 100;
            seed->coeffs[1] = 94;
            seed->coeffs[2] = 100;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 103) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 18;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 102;
            seed->coeffs[1] = 74;
            seed->coeffs[2] = 41;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 107) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 58;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 106;
            seed->coeffs[1] = 16;
            seed->coeffs[2] = 12;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 109) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 61;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 108;
            seed->coeffs[1] = 108;
            seed->coeffs[2] = 107;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 113) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 26;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 112;
            seed->coeffs[1] = 98;
            seed->coeffs[2] = 80;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 127) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 38;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 126;
            seed->coeffs[1] = 62;
            seed->coeffs[2] = 12;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 131) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 109;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 130;
            seed->coeffs[1] = 17;
            seed->coeffs[2] = 12;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 137) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 37;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 136;
            seed->coeffs[1] = 34;
            seed->coeffs[2] = 55;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 139) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 91;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 138;
            seed->coeffs[1] = 60;
            seed->coeffs[2] = 20;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 149) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 67;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 148;
            seed->coeffs[1] = 130;
            seed->coeffs[2] = 107;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 151) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 90;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 150;
            seed->coeffs[1] = 37;
            seed->coeffs[2] = 25;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 157) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 34;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 156;
            seed->coeffs[1] = 94;
            seed->coeffs[2] = 134;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 163) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 42;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 162;
            seed->coeffs[1] = 41;
            seed->coeffs[2] = 152;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 167) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 44;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 166;
            seed->coeffs[1] = 58;
            seed->coeffs[2] = 133;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 173) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 32;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 172;
            seed->coeffs[1] = 162;
            seed->coeffs[2] = 10;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 179) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 109;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 178;
            seed->coeffs[1] = 62;
            seed->coeffs[2] = 2;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 181) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 42;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 180;
            seed->coeffs[1] = 104;
            seed->coeffs[2] = 75;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 191) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 12;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 190;
            seed->coeffs[1] = 156;
            seed->coeffs[2] = 185;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 193) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 62;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 192;
            seed->coeffs[1] = 173;
            seed->coeffs[2] = 154;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 197) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 14;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 196;
            seed->coeffs[1] = 50;
            seed->coeffs[2] = 85;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 199) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 65;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 198;
            seed->coeffs[1] = 129;
            seed->coeffs[2] = 97;
            seed->coeffs[3] = 1;
        }
    }
    if (p == 30011) {
        if (m == 2) {
            seed = poly_create(2);
            seed->coeffs[0] = 1;
            seed->coeffs[1] = 24064;
            seed->coeffs[2] = 1;
        }
        if (m == 3) {
            seed = poly_create(3);
            seed->coeffs[0] = 30010;
            seed->coeffs[1] = 24058;
            seed->coeffs[2] = 23058;
            seed->coeffs[3] = 1;
        }
    }
    return seed;
}
