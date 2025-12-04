#include <stdio.h>
#include <assert.h>
#include "../core/include/dickson.h"

int main() {
    printf("=== Verifying Lifting Logic against Paper Example 1 (p=13) ===\n");

    // 1. 初始化 p=13, e=2
    dickson_int p = 13;
    int e = 2;
    DicksonContext *ctx = dickson_init(p, e);
    
    printf("V(x): ");
    dickson_print_vx(ctx);

    // 2. 初始种子 (来自论文 Step 2)
    dickson_int s_1 = 3;
    printf("Initial Seed S^(1): %lld\n", s_1);

    // 3. 计算导数 V'(3) mod 13
    dickson_int v_prime = dickson_eval_v_prime(ctx, s_1, p);
    printf("V'(3) mod 13: %lld (Expected: 6)\n", v_prime);
    assert(v_prime == 6);

    // 4. 计算 Update Factor C = -[V']^-1 mod 13
    dickson_int inv_v_prime = dickson_mod_inverse(v_prime, p);
    // C = -inv
    dickson_int C = (p - inv_v_prime) % p;
    printf("Update Factor C: %lld (Expected: 2)\n", C);
    assert(C == 2);

    // 5. 执行 Lifting Step
    // h=1, current_mod = 13^1 = 13
    dickson_int s_2 = dickson_lift_step(ctx, s_1, C, p);
    
    printf("Lifted Seed S^(2): %lld (Expected: 29)\n", s_2);
    
    if (s_2 == 29) {
        printf("\n✅ SUCCESS: Calculated value matches Paper exactly!\n");
    } else {
        printf("\n❌ FAILURE: Mismatch!\n");
        return 1;
    }

    dickson_free(ctx);
    return 0;
}