#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "dickson.h"

// --- 参数配置结构体 ---
typedef struct {
    dickson_int p;
    int e;
    dickson_int s_base;
    dickson_int a_base;
    int mode_auto;      // 1: Auto-Seed, 0: Manual
    int mode_full;      // 1: Generate all factors
    int silent;         // 1: Do not print factors to stdout
    char *output_file;  // Filename to write factors (NULL if none)
} Config;

void print_usage(const char* prog_name) {
    printf("Usage:\n");
    printf("  %s <p> <e> [options] <seed_args>\n", prog_name);
    printf("\n");
    printf("Options:\n");
    printf("  --auto            : Auto-search for seed (Benchmark mode)\n");
    printf("  --full <a_seed>   : Full factorization with manual seed\n");
    printf("  --silent          : Suppress factor printing (show stats only)\n");
    printf("  --output <file>   : Write factors to specified file\n");
    printf("\n");
    printf("Seed Args (Verification Mode):\n");
    printf("  <s_seed> [a_seed] : Single step verification if no --auto/--full set\n");
}

// 简单的参数解析器
int parse_args(int argc, char *argv[], Config *cfg) {
    if (argc < 3) return 0;
    
    cfg->p = atoll(argv[1]);
    cfg->e = atoi(argv[2]);
    cfg->mode_auto = 0;
    cfg->mode_full = 0;
    cfg->silent = 0;
    cfg->output_file = NULL;
    
    // 默认值
    cfg->s_base = 0;
    cfg->a_base = 0;

    // 遍历剩余参数
    for (int i = 3; i < argc; i++) {
        if (strcmp(argv[i], "--auto") == 0) {
            cfg->mode_auto = 1;
            cfg->mode_full = 1; // Auto implies full
        } else if (strcmp(argv[i], "--full") == 0) {
            cfg->mode_full = 1;
            if (i + 1 < argc && argv[i+1][0] != '-') {
                cfg->a_base = atoll(argv[++i]);
            } else {
                fprintf(stderr, "Error: --full requires a seed value.\n");
                return 0;
            }
        } else if (strcmp(argv[i], "--silent") == 0) {
            cfg->silent = 1;
        } else if (strcmp(argv[i], "--output") == 0) {
            if (i + 1 < argc) {
                cfg->output_file = argv[++i];
            } else {
                fprintf(stderr, "Error: --output requires a filename.\n");
                return 0;
            }
        } else {
            // 假设是 Verification 模式的种子
            if (cfg->s_base == 0) cfg->s_base = atoll(argv[i]);
            else if (cfg->a_base == 0) cfg->a_base = atoll(argv[i]);
        }
    }
    return 1;
}

// 辅助：打印因子 (到 stdout 或文件)
void print_factor(FILE *fp, int idx, dickson_int coeff, dickson_int mod) {
    // 打印格式：[idx] (x^2 + coeff*x + 1)
    // 为了美观，如果不为 0，才打印系数
    fprintf(fp, "[%d] (x^2 + %lldx + 1)\n", idx, coeff);
}

// --- 改造后的全量分解逻辑 (支持输出重定向) ---
void run_full_factorization(DicksonContext *ctx, dickson_int a_base_fp, Config *cfg) {
    // 1. 初始化
    dickson_int a1_sq = (a_base_fp * a_base_fp) % ctx->p;
    dickson_int s_base = (2 - a1_sq);
    while (s_base < 0) s_base += ctx->p;
    s_base %= ctx->p;

    if (!cfg->silent) printf("Step 1: Initializing from seed A^(1)=%lld -> S^(1)=%lld\n", a_base_fp, s_base);

    // 2. Lifting S
    dickson_int s_final = dickson_lift_seed(ctx, s_base);
    
    // 3. Recover A
    dickson_int a1_final = dickson_recover_a(ctx, s_final, a_base_fp);
    
    dickson_int mod = ctx->p;
    for(int i=1; i<ctx->e; i++) mod *= ctx->p;

    if (!cfg->silent) {
        printf("Step 2: Lifted Generator A_1 = %lld (mod %lld)\n", a1_final, mod);
        printf("Step 3: Generating all factors...\n");
        printf("========================================================\n");
    }

    // 4. 准备输出流
    FILE *out = stdout;
    if (cfg->output_file) {
        out = fopen(cfg->output_file, "w");
        if (!out) {
            fprintf(stderr, "Error: Cannot open output file %s\n", cfg->output_file);
            return;
        }
    }

    // 只有在非 silent 或者 指定了文件时，才执行打印循环
    if (!cfg->silent || cfg->output_file) {
        if (!cfg->output_file) printf("Full Factorization:\n"); // 只在屏幕打印时加标题
        
        fprintf(out, "[1] (x - 1)\n");
        fprintf(out, "[2] (x + 1)\n");
        int count = 2;
        
        if (ctx->p % 4 == 3) {
            fprintf(out, "[%d] (x^2 + 1)\n", ++count);
        }

        dickson_int d_prev = 2;
        dickson_int d_curr = a1_final;
        
        // i=1
        fprintf(out, "[%d] (x^2 + %lldx + 1)\n", ++count, (mod - d_curr) % mod);
        fprintf(out, "[%d] (x^2 + %lldx + 1)\n", ++count, d_curr);
        
        for (int i = 2; i <= ctx->k; i++) {
            dickson_int term = dickson_mod_mul(a1_final, d_curr, mod);
            dickson_int d_next = (term - d_prev) % mod;
            if (d_next < 0) d_next += mod;
            
            fprintf(out, "[%d] (x^2 + %lldx + 1)\n", ++count, (mod - d_next) % mod);
            fprintf(out, "[%d] (x^2 + %lldx + 1)\n", ++count, d_next);
            
            d_prev = d_curr;
            d_curr = d_next;
        }
        
        if (!cfg->silent) printf("Total Factors: %d\n", count);
    } else {
        // Silent mode: 只计算数量
        int count = 2;
        if (ctx->p % 4 == 3) count++;
        count += 2 * ctx->k;
        printf("Total Factors: %d\n", count);
    }

    if (cfg->output_file && out) fclose(out);
}

int main(int argc, char *argv[]) {
    // [新增] 计时开始
    clock_t start_time = clock();

    srand((unsigned int)time(NULL));
    Config cfg;
    
    if (!parse_args(argc, argv, &cfg)) {
        print_usage(argv[0]);
        return 1;
    }

    DicksonContext *ctx = dickson_init(cfg.p, cfg.e);
    if (!ctx) return 1;

    if (!cfg.silent) {
        printf("=== Dickson-Engine ===\n");
        printf("Prime: %lld, Precision: %d\n", cfg.p, cfg.e);
        if (cfg.output_file) printf("Output File: %s\n", cfg.output_file);
        printf("------------------------------------------\n");
    }

    if (cfg.mode_full) {
        dickson_int a_seed = cfg.a_base;
        if (cfg.mode_auto) {
            a_seed = dickson_find_random_seed(ctx);
            if (a_seed == 0) return 1;
        }
        
        // 这里的 run_full_factorization 包含了主要的计算逻辑
        // 注意：这里的计时也包含了 find_random_seed 的时间，这对 NTL 是公平的
        run_full_factorization(ctx, a_seed, &cfg);
        
    } else {
        // Verification Mode
        if (!cfg.silent) {
            printf("Verification Mode (Single Seed)\n");
            dickson_print_vx(ctx);
        }
        dickson_int s_final = dickson_lift_seed(ctx, cfg.s_base);
        if (!cfg.silent) printf("S_final = %lld\n", s_final);
        
        if (cfg.a_base != 0) {
            dickson_int a_final = dickson_recover_a(ctx, s_final, cfg.a_base);
            if (!cfg.silent) printf("Recovered A = %lld\n", a_final);
        }
    }

    dickson_free(ctx);

    // [新增] 计时结束与输出
    clock_t end_time = clock();
    double elapsed_s = (double)(end_time - start_time) / CLOCKS_PER_SEC;

    // 格式必须和 NTL_bench 保持一致，方便 Python 解析
    if (!cfg.silent) printf("------------------------------------------\n");
    // 即便是 silent 模式，我们通常也需要输出时间给跑分脚本抓取
    // 但为了纯净，我们可以只在 silent 模式下输出这一行，或者标准输出
    // 为了简单，我们始终打印时间
    printf("Time Elapsed       : %.6f s\n", elapsed_s);
    if (!cfg.silent) printf("==========================================\n");

    return 0;
}
