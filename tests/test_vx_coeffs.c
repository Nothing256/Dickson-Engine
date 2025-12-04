#include <stdio.h>
#include "../core/include/dickson.h"

int main() {
    printf("=== Verifying V(x) Construction against Paper (Page 8) ===\n\n");

    // Case 1: p = 13 (4k+1, k=3)
    // Paper: x^3 - x^2 - 2x + 1
    DicksonContext *ctx13 = dickson_init(13, 1);
    dickson_print_vx(ctx13);
    
    // Case 2: p = 17 (4k+1, k=4)
    // Paper: x^4 - x^3 - 3x^2 + 2x + 1
    DicksonContext *ctx17 = dickson_init(17, 1);
    dickson_print_vx(ctx17);

    // Case 3: p = 29 (4k+1, k=7)
    // Paper: x^7 - x^6 - 6x^5 + 5x4 + 10x^3 - 6x^2 - 4x + 1
    DicksonContext *ctx29 = dickson_init(29, 1);
    dickson_print_vx(ctx29);
    
    // Extra Case from Definition 2: p = 7 (4k+3, k=1)
    // V_0 = C(1,0) = 1
    // V_1 = 0
    // Expected: x
    DicksonContext *ctx7 = dickson_init(7, 1);
    dickson_print_vx(ctx7);

    dickson_free(ctx13);
    dickson_free(ctx17);
    dickson_free(ctx29);
    dickson_free(ctx7);
    
    return 0;
}