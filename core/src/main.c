#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dickson.h"

void print_usage(const char* prog_name) {
    printf("Usage: %s <p> <e> <seed_s> [seed_a]\n", prog_name);
    printf("  p      : Prime number (must be > 2)\n");
    printf("  e      : Target precision exponent\n");
    printf("  seed_s : Initial structural seed S^(1) in Fp\n");
    printf("  seed_a : (Optional) Initial coefficient A^(1) to recover factor\n");
    printf("\nExample 1 (Paper Exp 1): %s 13 2 3 5\n", prog_name);
    printf("Example 2 (Paper Exp 2): %s 19 3 4 6\n", prog_name);
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_usage(argv[0]);
        return 1;
    }

    // 1. 解析基础参数
    dickson_int p = atoll(argv[1]);
    int e = atoi(argv[2]);
    dickson_int s_base = atoll(argv[3]);
    
    // 2. 解析可选参数 (用于恢复 A)
    dickson_int a_base = 0;
    int recover_mode = 0;
    if (argc >= 5) {
        a_base = atoll(argv[4]);
        recover_mode = 1;
    }

    printf("=== Dickson-Engine: Explicit Factorization ===\n");
    printf("Configuration:\n");
    printf("  Prime p : %lld\n", p);
    printf("  Target e: %d\n", e);
    printf("  Seed S  : %lld\n", s_base);
    if (recover_mode) {
        printf("  Seed A  : %lld (Recovery Mode ON)\n", a_base);
    }
    printf("------------------------------------------\n");

    // 3. 初始化引擎 (这里定义了 ctx)
    DicksonContext *ctx = dickson_init(p, e);
    if (!ctx) {
        fprintf(stderr, "Error: Failed to initialize context.\n");
        return 1;
    }

    printf("Generated V(x): ");
    dickson_print_vx(ctx);
    printf("------------------------------------------\n");

    // 4. 执行 Lifting (这里定义了 s_final)
    printf("Starting Lifting Process for S...\n");
    dickson_int s_final = dickson_lift_seed(ctx, s_base);

    // 5. 输出 S 的结果
    printf("------------------------------------------\n");
    printf("Final Result over Z_{p^%d}:\n", e);
    printf("Structural S = %lld\n", s_final);
    
    // 6. 执行 A 的恢复 (如果开启)
    if (recover_mode) {
        printf("------------------------------------------\n");
        printf("Recovering Factor Coefficient A...\n");
        printf("Constraint: A^2 = 2 - S (mod p^e)\n");
        
        dickson_int a_final = dickson_recover_a(ctx, s_final, a_base);
        
        printf("Recovered A  = %lld\n", a_final);
        
        // --- 验证逻辑 ---
        
        // 验证 Example 1
        // P=13, E=2. Factors: x^2 ± 135x + 1. 
        // 135 mod 169 is 135. Also -135 mod 169 is 34.
        if (p == 13 && e == 2 && (a_final == 135 || a_final == 34)) {
             printf("\n[Verification] Matches Paper Example 1 Factor! ✅\n");
        }
        
        // 验证 Example 2
        // P=19, E=3. Factors: x^2 ± 6618x + 1.
        if (p == 19 && e == 3 && a_final == 6618) {
             printf("\n[Verification] Matches Paper Example 2 Factor! ✅\n");
        }
    } else {
        // 如果没开 A 恢复模式，只验证 S
        if (p == 13 && e == 2 && s_final == 29) {
            printf("\n[Verification] Matches Paper Example 1 (S only)! ✅\n");
        }
        if (p == 19 && e == 3 && s_final == 3652) {
             printf("\n[Verification] Matches Paper Example 2 (S only)! ✅\n");
        }
    }

    dickson_free(ctx);
    return 0;
}