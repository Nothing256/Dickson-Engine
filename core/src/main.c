#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h> // 用于随机种子
#include "dickson.h"

void print_usage(const char* prog_name) {
    printf("Usage:\n");
    printf("  1. Verification Mode:\n");
    printf("     %s <p> <e> <s_seed> [a_seed]\n", prog_name);
    printf("  2. Full Factorization (Manual Seed):\n");
    printf("     %s <p> <e> --full <a_seed>\n", prog_name);
    printf("  3. Full Factorization (Auto Seed - FAIR Benchmark):\n");
    printf("     %s <p> <e> --auto\n", prog_name);
}

int main(int argc, char *argv[]) {
    // 初始化随机数种子
    srand((unsigned int)time(NULL));

    if (argc < 3) { // 至少需要 p 和 e
        print_usage(argv[0]);
        return 1;
    }

    dickson_int p = atoll(argv[1]);
    int e = atoi(argv[2]);
    
    // 检查模式
    int full_mode = 0;
    int auto_mode = 0;
    
    if (argc >= 4) {
        if (strcmp(argv[3], "--auto") == 0) {
            full_mode = 1;
            auto_mode = 1;
        } else if (strcmp(argv[3], "--full") == 0) {
            full_mode = 1;
        }
    }

    DicksonContext *ctx = dickson_init(p, e);
    if (!ctx) return 1;

    printf("=== Dickson-Engine: Explicit Factorization ===\n");
    printf("Mode: %s\n", auto_mode ? "Auto-Seed (Benchmark Ready)" : "Manual Seed");
    printf("Prime: %lld, Precision: %d\n", p, e);
    printf("------------------------------------------\n");

    if (full_mode) {
        dickson_int a_seed = 0;
        
        if (auto_mode) {
            // --- 自动搜索模块 ---
            // 这里的时间会被计入总耗时，对 NTL 比较公平
            a_seed = dickson_find_random_seed(ctx);
            if (a_seed == 0) return 1;
        } else {
            if (argc < 5) {
                fprintf(stderr, "Error: Manual full mode requires a_seed.\n");
                return 1;
            }
            a_seed = atoll(argv[4]);
        }
        
        dickson_factorize_full(ctx, a_seed);
        
    } else {
        // ... (保留旧的 Verification 逻辑) ...
        // 为了简洁，这里就不重复贴了，保持你原来的 Verification 代码即可
        // 只需要注意 argv[3] 不是 --auto 也不是 --full 时进入这里
        if (argc >= 4 && argv[3][0] != '-') {
             dickson_int s_base = atoll(argv[3]);
             // ... 原有逻辑
             // 简易处理：直接把原代码 copy 过来
             printf("Generated V(x): ");
             dickson_print_vx(ctx);
             dickson_int s_final = dickson_lift_seed(ctx, s_base);
             printf("Structural S = %lld\n", s_final);
             if (argc >= 5) {
                 dickson_int a_final = dickson_recover_a(ctx, s_final, atoll(argv[4]));
                 printf("Recovered A = %lld\n", a_final);
             }
        }
    }

    dickson_free(ctx);
    return 0;
}