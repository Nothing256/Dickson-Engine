#ifndef DICKSON_H
#define DICKSON_H

#include <stdint.h>

// 基础类型定义：目前使用原生 64 位整数
// Future Roadmap: GMP implementation for cryptographic scale
typedef unsigned long long dickson_int;

/**
 * 核心结构体：用于封装 V(x) 相关的参数
 */
typedef struct {
    dickson_int p;
    int e;
    int k; // k = floor(p/4)
} DicksonContext;

// 函数声明原型 (TODO)
dickson_int dickson_poly_val(dickson_int x, dickson_int mod);
dickson_int get_update_factor(dickson_int s, dickson_int p);

#endif // DICKSON_H
