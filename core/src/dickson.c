#include "dickson.h"
#include <stdio.h>
#include <string.h>

/**
 * 内部辅助：使用帕斯卡三角生成二项式系数 C(n, k)
 * 注意：仅用于演示和小规模计算。
 * 对于大规模计算，未来将替换为 GMP 版本。
 */
static dickson_int binomial_coeff(int n, int k) {
    if (k < 0 || k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n / 2) k = n - k;
    
    // 使用简单的乘法防止溢出 (适用于 n 较小的情况)
    // 实际工程中这里可以使用 memoization 或者预计算表
    dickson_int res = 1;
    for (int i = 1; i <= k; ++i) {
        res = res * (n - i + 1) / i;
    }
    return res;
}

DicksonContext* dickson_init(dickson_int p, int e) {
    DicksonContext *ctx = (DicksonContext*)malloc(sizeof(DicksonContext));
    if (!ctx) return NULL;

    ctx->p = p;
    ctx->e = e;
    ctx->k = p / 4;
    ctx->degree = ctx->k;
    
    // 分配系数数组 (x^k 到 x^0，共 k+1 项)
    ctx->coeffs = (dickson_int*)calloc(ctx->degree + 1, sizeof(dickson_int));
    if (!ctx->coeffs) {
        free(ctx);
        return NULL;
    }

    // 根据论文 Definition 2 生成系数
    // V(x) = sum V_r * x^{k-r}
    // r 对应数组下标 index
    
    // 判断 p mod 4 的情况
    int is_4k_plus_1 = (p % 4 == 1);

    for (int r = 0; r <= ctx->degree; r++) {
        // 我们遍历 r (即论文中的下标)
        // 系数 V_r 取决于 r 是偶数(2i) 还是 奇数(2i+1)
        
        int i = r / 2;
        dickson_int sign = (i % 2 == 0) ? 1 : -1; // (-1)^i
        dickson_int binom = 0;
        
        if (r % 2 == 0) {
            // Case V_{2i}
            // 无论是 4k+1 还是 4k+3，公式都是 (-1)^i * C(k-i, i)
            binom = binomial_coeff(ctx->k - i, i);
            ctx->coeffs[r] = sign * binom;
        } else {
            // Case V_{2i+1}
            if (!is_4k_plus_1) {
                // p = 4k+3: V_{2i+1} = 0
                ctx->coeffs[r] = 0;
            } else {
                // p = 4k+1: V_{2i+1} = (-1)^{i+1} * C(k-i-1, i)
                sign = ((i + 1) % 2 == 0) ? 1 : -1; // 注意这里是 (-1)^{i+1}
                binom = binomial_coeff(ctx->k - i - 1, i);
                ctx->coeffs[r] = sign * binom;
            }
        }
    }

    return ctx;
}

void dickson_free(DicksonContext* ctx) {
    if (ctx) {
        if (ctx->coeffs) free(ctx->coeffs);
        free(ctx);
    }
}

void dickson_print_vx(DicksonContext* ctx) {
    printf("V(x) for p=%lld (k=%d): ", ctx->p, ctx->k);
    for (int r = 0; r <= ctx->degree; r++) {
        dickson_int c = ctx->coeffs[r];
        if (c == 0) continue;
        
        // 处理符号
        if (r == 0) {
            if (c < 0) printf("-");
        } else {
            printf(c >= 0 ? " + " : " - ");
        }
        
        // 处理绝对值
        long long abs_c = c >= 0 ? c : -c;
        if (abs_c != 1 || (ctx->degree - r) == 0) printf("%lld", abs_c);
        
        // 处理 x 的幂
        int power = ctx->degree - r;
        if (power > 0) {
            printf("x");
            if (power > 1) printf("^%d", power);
        }
    }
    printf("\n");
}