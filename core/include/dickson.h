#ifndef DICKSON_H
#define DICKSON_H

#include <stdint.h>
#include <stdlib.h>

// 基础类型
typedef long long dickson_int;

/**
 * 核心结构体
 */
typedef struct {
    dickson_int p;     
    int e;             
    int k;             // k = floor(p/4)
    int degree;        
    dickson_int *coeffs; 
} DicksonContext;

// --- 初始化与销毁 ---
DicksonContext* dickson_init(dickson_int p, int e);
void dickson_free(DicksonContext* ctx);
void dickson_print_vx(DicksonContext* ctx);

// --- 基础工具 ---
dickson_int dickson_mod_mul(dickson_int a, dickson_int b, dickson_int m);
dickson_int dickson_mod_inverse(dickson_int a, dickson_int m);

// --- 核心算法组件 ---
dickson_int dickson_eval_v(DicksonContext *ctx, dickson_int x, dickson_int m);
dickson_int dickson_eval_v_prime(DicksonContext *ctx, dickson_int x, dickson_int m);
dickson_int dickson_lift_step(DicksonContext *ctx, dickson_int s_old, dickson_int update_factor, dickson_int current_p_pow);
dickson_int dickson_lift_seed(DicksonContext *ctx, dickson_int s_base);
dickson_int dickson_recover_a(DicksonContext *ctx, dickson_int s_final, dickson_int a_base);

// --- 全量生产模式 ---
/**
 * 全量因式分解模式
 * 1. 自动计算 S_base = 2 - a_base^2
 * 2. 提升 S
 * 3. 恢复 A_1
 * 4. 递归生成所有 A_i 并打印因子
 */
void dickson_factorize_full(DicksonContext *ctx, dickson_int a_base_fp);

#endif // DICKSON_H