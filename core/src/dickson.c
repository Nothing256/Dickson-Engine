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




// --- 基础算术实现 ---

// 扩展欧几里得算法: ax + by = gcd(a, b)
static dickson_int xgcd(dickson_int a, dickson_int b, dickson_int *x, dickson_int *y) {
    if (a == 0) {
        *x = 0;
        *y = 1;
        return b;
    }
    dickson_int x1, y1;
    dickson_int gcd = xgcd(b % a, a, &x1, &y1);
    *x = y1 - (b / a) * x1;
    *y = x1;
    return gcd;
}

dickson_int dickson_mod_inverse(dickson_int a, dickson_int m) {
    dickson_int x, y;
    dickson_int g = xgcd(a, m, &x, &y);
    if (g != 1) return 0; // 逆不存在
    return (x % m + m) % m;
}

dickson_int dickson_mod_mul(dickson_int a, dickson_int b, dickson_int m) {
    // 简单实现。注意：如果 a*b 超过 2^63，这里会溢出。
    // 在纯手写版中，我们假设 p^e 在 long long 范围内。
    // 如果需要更稳健，可以用 __int128 (gcc扩展) 或拆分乘法。
#ifdef __SIZEOF_INT128__
    return (dickson_int)(((__int128)a * b) % m);
#else
    return (a * b) % m; 
#endif
}

// --- 多项式操作实现 ---

// 霍纳法则计算 V(x)
dickson_int dickson_eval_v(DicksonContext *ctx, dickson_int x, dickson_int m) {
    dickson_int res = 0;
    // 从高次项开始遍历: coeffs[0]*x^k + ...
    for (int i = 0; i <= ctx->degree; i++) {
        res = dickson_mod_mul(res, x, m);
        
        dickson_int c = ctx->coeffs[i];
        // 处理负数系数的模运算
        dickson_int c_mod = c % m;
        if (c_mod < 0) c_mod += m;
        
        res = (res + c_mod) % m;
    }
    return res;
}

// 计算 V'(x)。注意：我们需要根据系数手动计算导数多项式的值
// V(x) = sum c_i * x^{k-i}
// V'(x) = sum c_i * (k-i) * x^{k-i-1}
dickson_int dickson_eval_v_prime(DicksonContext *ctx, dickson_int x, dickson_int m) {
    dickson_int res = 0;
    for (int i = 0; i < ctx->degree; i++) { // 常数项导数为0，所以只遍历到 degree-1
        int power = ctx->degree - i; // 当前项是 x^power
        // 导数系数 = coeff * power
        
        res = dickson_mod_mul(res, x, m);
        
        dickson_int c = ctx->coeffs[i];
        dickson_int der_c = c * power; // 可能会很大，先不模
        
        dickson_int der_c_mod = der_c % m;
        if (der_c_mod < 0) der_c_mod += m;
        
        res = (res + der_c_mod) % m;
    }
    return res;
}

// --- 核心 Lifting 逻辑 ---

dickson_int dickson_lift_step(DicksonContext *ctx, dickson_int s_old, dickson_int update_factor, dickson_int current_p_pow) {
    // 算法逻辑：
    // 1. 计算 Lifting Error: Delta = V(s_old) / p^h
    //    注意：我们需要在更高的精度下计算 V(s_old)。
    //    精度至少要是 p^{h+1}，或者简单地用 current_p_pow * ctx->p
    
    dickson_int next_mod = current_p_pow * ctx->p;
    
    // 计算 V(s_old) mod p^{h+1}
    dickson_int v_val = dickson_eval_v(ctx, s_old, next_mod);
    
    // 理论上 v_val 应该是 p^h 的倍数 (即 V(s) = 0 mod p^h)
    // Delta = v_val / p^h
    dickson_int delta = v_val / current_p_pow;
    
    // 2. 计算调整量 Adjustment = (C * Delta) mod p
    // update_factor 就是预计算好的 C_i
    dickson_int adjustment = dickson_mod_mul(update_factor, delta, ctx->p);
    
    // 3. 更新 S_new = S_old + adjustment * p^h
    dickson_int step_val = adjustment * current_p_pow;
    dickson_int s_new = s_old + step_val;
    
    return s_new; // 返回的值不需要模 next_mod，因为它本身就在范围内
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


// --- 高级 API 实现 ---

dickson_int dickson_lift_seed(DicksonContext *ctx, dickson_int s_base) {
    // 1. 预计算 (Pre-computation)
    // 计算导数 V'(s_base) mod p
    dickson_int v_prime = dickson_eval_v_prime(ctx, s_base, ctx->p);
    
    // 计算不变因子 C = -[V'(s)]^-1 mod p
    dickson_int inv = dickson_mod_inverse(v_prime, ctx->p);
    if (inv == 0) {
        fprintf(stderr, "Error: V'(s) is not invertible! Singular root?\n");
        return -1; 
    }
    dickson_int C = (ctx->p - inv) % ctx->p;
    
    // 2. 迭代 Lifting (Loop)
    dickson_int current_s = s_base;
    dickson_int current_p_pow = ctx->p; // p^1
    
    // 我们从 h=1 开始 lift 到 h=e-1 (即 lift 到 p^e)
    for (int h = 1; h < ctx->e; h++) {
        // 调用我们刚才验证过的核心单步函数
        current_s = dickson_lift_step(ctx, current_s, C, current_p_pow);
        
        // 更新 p 的幂次 (p^h -> p^{h+1})
        current_p_pow *= ctx->p;
    }
    
    return current_s;
}


// --- 系数恢复逻辑 (Recover A from S) ---

/**
 * 使用牛顿迭代法提升平方根
 * 求解 x^2 = val (mod p^e)
 * 初始猜测: x_base (满足 x_base^2 = val mod p)
 */
dickson_int dickson_lift_sqrt(DicksonContext *ctx, dickson_int val, dickson_int x_base) {
    dickson_int current_x = x_base;
    dickson_int current_mod = ctx->p;
    
    // 牛顿迭代公式: x_new = (x_old + val * x_old^-1) * 2^-1
    // 或者更简单的形式: x_new = x_old - (x_old^2 - val) / (2*x_old)
    
    // 我们需要计算 2^-1 mod p^e (因为 p 是奇素数，所以 2 永远可逆)
    // 实际上我们在每一步 mod p^k 下计算即可
    
    for (int h = 1; h < ctx->e; h++) {
        dickson_int next_mod = current_mod * ctx->p;
        
        // 1. 计算分子 num = x^2 - val
        // 注意：这里需要大数乘法，如果不使用 __int128，要注意溢出
        // 简单起见，我们假设 x^2 在 long long 范围内，或者我们只计算 error term
        
        // error = (x^2 - val)
        // 这里的运算需要在 next_mod 下进行，甚至更大
        
        // 为了安全，我们用下面的变体公式，避免直接算 x^2
        // x_{k+1} = x_k + adjustment
        // adjustment = - (x_k^2 - val) * (2*x_k)^-1
        
        dickson_int x_sq = dickson_mod_mul(current_x, current_x, next_mod);
        dickson_int diff = (x_sq - (val % next_mod));
        if (diff < 0) diff += next_mod;
        
        // 2. 计算分母 den = 2 * x_k
        dickson_int den = (2 * current_x) % next_mod;
        
        // 3. 计算分母的逆 den^-1 mod p (注意：Hensel提升只需要模 p 的逆即可计算调整量!)
        // 这是一个关键的优化点，Hensel Lemma 的梯度只需要低精度的逆
        dickson_int den_inv = dickson_mod_inverse(den % ctx->p, ctx->p);
        
        // 4. 计算调整量 u = - diff / den
        // 实际上是 u = - (diff / p^h) * den_inv mod p
        // 我们利用整数除法特性
        
        if (diff % current_mod != 0) {
             fprintf(stderr, "Error: Newton lift failed, internal precision error.\n");
             return 0;
        }
        
        dickson_int diff_scaled = diff / current_mod; // 这是一个小整数
        dickson_int adjustment_factor = dickson_mod_mul(diff_scaled, den_inv, ctx->p);
        dickson_int adjustment = (ctx->p - adjustment_factor) % ctx->p;
        
        // 5. 更新
        current_x = current_x + adjustment * current_mod;
        current_mod = next_mod;
    }
    
    return current_x;
}

dickson_int dickson_recover_a(DicksonContext *ctx, dickson_int s_final, dickson_int a_base) {
    // 目标: 解 A^2 = 2 - S (mod p^e)
    
    // 1. 计算目标值 R = 2 - S
    // 注意处理负数
    dickson_int final_mod = ctx->p;
    for(int i=1; i<ctx->e; i++) final_mod *= ctx->p;
    
    dickson_int val = (2 - s_final) % final_mod;
    if (val < 0) val += final_mod;
    
    // 2. 调用通用的开方提升
    return dickson_lift_sqrt(ctx, val, a_base);
}



// --- [NEW] 全量因式分解实现 ---

void dickson_factorize_full(DicksonContext *ctx, dickson_int a_base_fp) {
    // 1. 准备阶段：从用户给的 Fp 种子 A 计算出结构种子 S
    // S^(1) = 2 - (A^(1))^2 mod p
    dickson_int a1_sq = (a_base_fp * a_base_fp) % ctx->p;
    dickson_int s_base = (2 - a1_sq);
    while (s_base < 0) s_base += ctx->p; // 确保正数
    s_base %= ctx->p;

    printf("Step 1: Initializing from seed A^(1)=%lld -> S^(1)=%lld\n", a_base_fp, s_base);

    // 2. 核心提升 (Lifting S) - O(e*p)
    // 这里调用我们之前写好的逻辑
    dickson_int s_final = dickson_lift_seed(ctx, s_base);
    
    // 3. 恢复 A_1 (Recover A) - O(e)
    // 使用牛顿迭代
    dickson_int a1_final = dickson_recover_a(ctx, s_final, a_base_fp);
    
    // 计算最终的大模数 M = p^e
    dickson_int mod = ctx->p;
    for(int i=1; i<ctx->e; i++) mod *= ctx->p;

    printf("Step 2: Lifted Generator A_1 = %lld (mod %lld)\n", a1_final, mod);
    printf("Step 3: Generating all factors via Dickson Recurrence...\n");
    printf("========================================================\n");
    printf("Full Factorization of x^%lld - 1 over Z_{%lld}:\n", ctx->p + 1, mod);
    
    // 4. 打印固定因子
    printf("[1] (x - 1)\n");
    printf("[2] (x + 1)\n");
    

    int count = 2;
    
    // 处理 x^2 + 1 (仅当 p = 4k + 3 时存在)
    if (ctx->p % 4 == 3) {
        printf("[%d] (x^2 + 1)\n", ++count);
    }

    // 5. 递归生成并打印所有二次因子对 (Pair)
    // Dickson Recurrence: D_i = A_1 * D_{i-1} - D_{i-2}
    
    dickson_int d_prev = 2;
    dickson_int d_curr = a1_final;
    
    // --- 处理第一项 A_1 (i=1) ---
    // Factor Pair: x^2 ± A_1 x + 1
    // 1. x^2 - A_1 x + 1  -> Coeff: (mod - A_1)
    printf("[%d] (x^2 + %lldx + 1)\n", ++count, (mod - d_curr) % mod);
    // 2. x^2 + A_1 x + 1  -> Coeff: A_1
    printf("[%d] (x^2 + %lldx + 1)\n", ++count, d_curr);
    
    // --- 循环生成剩余项 (i=2...k) ---
    for (int i = 2; i <= ctx->k; i++) {
        // 计算 D_i
        dickson_int term = dickson_mod_mul(a1_final, d_curr, mod);
        dickson_int d_next = (term - d_prev) % mod;
        if (d_next < 0) d_next += mod;
        
        // 打印一对因子
        // 1. x^2 - A_i x + 1
        printf("[%d] (x^2 + %lldx + 1)\n", ++count, (mod - d_next) % mod);
        // 2. x^2 + A_i x + 1
        printf("[%d] (x^2 + %lldx + 1)\n", ++count, d_next);
        
        // 更新状态
        d_prev = d_curr;
        d_curr = d_next;
    }
    
    printf("========================================================\n");
    printf("Total Factors: %d\n", count);
}



// --- [NEW] 自动搜寻种子 ---

// 快速幂: base^exp % mod
static dickson_int mod_pow(dickson_int base, dickson_int exp, dickson_int mod) {
    dickson_int res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = dickson_mod_mul(res, base, mod);
        base = dickson_mod_mul(base, base, mod);
        exp /= 2;
    }
    return res;
}

// 勒让德符号 (a/p)
// 返回 1 (Residue), -1 (Non-residue), 0 (Divisible)
static int legendre(dickson_int a, dickson_int p) {
    dickson_int res = mod_pow(a, (p - 1) / 2, p);
    if (res == p - 1) return -1;
    return (int)res;
}


dickson_int dickson_find_random_seed(DicksonContext *ctx) {
    dickson_int candidate = 0;
    
    // 分配标记数组
    char *flags = (char *)calloc(ctx->p + 1, sizeof(char));
    if (!flags) {
        fprintf(stderr, "Warning: Memory check failed.\n");
    }

    // 设定尝试上限
    for (int r = 0; r < 2000; r++) { // 稍微增加尝试次数，因为条件更严了
        // 1. 伪随机生成 a
        candidate = (rand() % (ctx->p - 3)) + 2; 
        
        // 2. 判别式检查 (不可约性)
        dickson_int D = (candidate * candidate) - 4;
        while (D < 0) D += ctx->p;
        D %= ctx->p;
        
        if (D == 0) continue; 
        if (legendre(D, ctx->p) != -1) continue; 

        // 3. [UPDATED] 序列完整性检查 (Integrity Check)
        // 必须确保 A_i 不等于 +/- 2，且 A_i 不等于 +/- A_j
        
        if (flags) {
            // 重置标记
            memset(flags, 0, (ctx->p + 1) * sizeof(char));
            
            int is_bad = 0;
            dickson_int d_prev = 2;
            dickson_int d_curr = candidate; // A_1
            
            for (int i = 1; i <= ctx->k; i++) {
                // A. 禁忌值检查: +/- 2
                if (d_curr == 2 || d_curr == ctx->p - 2) {
                    is_bad = 1; break;
                }
                
                // B. 碰撞检查: 检查 val 和 p-val 是否已存在
                if (flags[d_curr]) {
                    is_bad = 1; break;
                }
                
                // C. 标记当前值及其镜像
                // 这样如果后面出现了 -d_curr，也会被 B 步骤捕获
                flags[d_curr] = 1;
                flags[ctx->p - d_curr] = 1;
                
                // D. 递推
                if (i < ctx->k) {
                    dickson_int next = (candidate * d_curr - d_prev) % ctx->p;
                    if (next < 0) next += ctx->p;
                    d_prev = d_curr;
                    d_curr = next;
                }
            }
            
            if (is_bad) continue; // 这是一个“伪”本原根，跳过
        }

        // 4. 成功
        if (flags) free(flags);
        printf("Step 0: Found PRIMITIVE seed A^(1) = %lld (Passed Rigorous Integrity Check)\n", candidate);
        return candidate;
    }
    
    if (flags) free(flags);
    fprintf(stderr, "Warning: Could not find valid seed.\n");
    return 0; 
}