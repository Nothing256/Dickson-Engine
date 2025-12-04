#ifndef DICKSON_H
#define DICKSON_H

#include <stdint.h>
#include <stdlib.h>

// 基础类型：使用 64 位有符号整数 (为了处理系数的符号)
typedef long long dickson_int;

/**
 * 核心结构体：管理 V(x) 的上下文
 */
typedef struct {
    dickson_int p;     // 素数 p
    int e;             // 目标精度 e
    int k;             // k = floor(p/4)
    int degree;        // V(x) 的度数 (= k)
    dickson_int *coeffs; // V(x) 的系数数组: coeffs[0]*x^k + ... + coeffs[k]
} DicksonContext;

/**
 * 初始化上下文并生成 V(x) 的系数
 * @param p 素数
 * @param e 精度
 * @return 初始化好的上下文指针
 */
DicksonContext* dickson_init(dickson_int p, int e);

/**
 * 释放上下文
 */
void dickson_free(DicksonContext* ctx);

/**
 * 打印 V(x) 多项式 (用于 Debug 和验证)
 */
void dickson_print_vx(DicksonContext* ctx);



/**
 * 模块化算术工具
 */
dickson_int dickson_mod_mul(dickson_int a, dickson_int b, dickson_int m);
dickson_int dickson_mod_inverse(dickson_int a, dickson_int m);

/**
 * 多项式求值 (Horner's Method)
 * 计算 V(x) mod m
 */
dickson_int dickson_eval_v(DicksonContext *ctx, dickson_int x, dickson_int m);

/**
 * 多项式导数求值
 * 计算 V'(x) mod m
 */
dickson_int dickson_eval_v_prime(DicksonContext *ctx, dickson_int x, dickson_int m);

/**
 * 核心 Lifting 步骤 (单步)
 * 输入当前层的 S_old 和当前模数 current_mod (p^h)
 * 输出下一层的 S_new
 */
dickson_int dickson_lift_step(DicksonContext *ctx, dickson_int s_old, dickson_int update_factor, dickson_int current_p_pow);


/**
 * 完整 Lifting 流程
 * 输入：初始种子 s_base (在 Fp 域内)
 * 输出：提升到 Zpe 后的最终种子 S
 */
dickson_int dickson_lift_seed(DicksonContext *ctx, dickson_int s_base);


// ...
dickson_int dickson_lift_seed(DicksonContext *ctx, dickson_int s_base);

/**
 * 从 S 恢复 A
 * 求解 A^2 = 2 - S mod p^e，初始值为 a_base
 */
dickson_int dickson_recover_a(DicksonContext *ctx, dickson_int s_final, dickson_int a_base);
// ...

#endif // DICKSON_H