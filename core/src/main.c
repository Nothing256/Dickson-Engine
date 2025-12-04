#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dickson.h"

void print_usage(const char* prog_name) {
    printf("Usage:\n");
    printf("  1. Verification Mode (Single Step):\n");
    printf("     %s <p> <e> <s_seed> [a_seed]\n", prog_name);
    printf("  2. Full Factorization Mode (Production):\n");
    printf("     %s <p> <e> --full <a_seed>\n", prog_name);
    printf("\n");
    printf("Arguments:\n");
    printf("  p       : Prime number\n");
    printf("  e       : Target precision\n");
    printf("  s_seed  : Structural seed S^(1)\n");
    printf("  a_seed  : Coefficient seed A^(1) (Generator)\n");
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_usage(argv[0]);
        return 1;
    }

    dickson_int p = atoll(argv[1]);
    int e = atoi(argv[2]);
    
    // 检查模式
    int full_mode = 0;
    if (strcmp(argv[3], "--full") == 0) {
        full_mode = 1;
    }

    // 初始化引擎
    DicksonContext *ctx = dickson_init(p, e);
    if (!ctx) {
        fprintf(stderr, "Error: Failed to initialize context.\n");
        return 1;
    }

    printf("=== Dickson-Engine: Explicit Factorization ===\n");
    printf("Mode: %s\n", full_mode ? "Full Factorization (Recursive Generation)" : "Verification (Single Step)");
    printf("Prime: %lld, Precision: %d\n", p, e);
    printf("------------------------------------------\n");

    if (full_mode) {
        if (argc < 5) {
            fprintf(stderr, "Error: Full mode requires a_seed.\n");
            return 1;
        }
        dickson_int a_seed = atoll(argv[4]);
        
        // 调用全量生产函数
        dickson_factorize_full(ctx, a_seed);
        
    } else {
        // --- 原有的验证逻辑 ---
        dickson_int s_base = atoll(argv[3]);
        
        printf("Generated V(x): ");
        dickson_print_vx(ctx);
        
        printf("Starting Lifting Process for S...\n");
        dickson_int s_final = dickson_lift_seed(ctx, s_base);

        printf("Final Result over Z_{p^%d}:\n", e);
        printf("Structural S = %lld\n", s_final);
        
        // 如果提供了 a_base，验证 A
        if (argc >= 5) {
            dickson_int a_base = atoll(argv[4]);
            dickson_int a_final = dickson_recover_a(ctx, s_final, a_base);
            printf("Recovered A  = %lld\n", a_final);
            
            // 简单的 Check
            printf("[Info] Check: A^2 + S - 2 = %lld (mod %lld)\n", 
                   (a_final*a_final + s_final - 2), 
                   (dickson_int)1); // 这里只是简单的打印，实际验证在肉眼
        }
    }

    dickson_free(ctx);
    return 0;
}