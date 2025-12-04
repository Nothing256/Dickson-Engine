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

#endif // DICKSON_H