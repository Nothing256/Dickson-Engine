#include <new> // 必须放在最前面解决 macOS 兼容性
#include <NTL/ZZ_pXFactoring.h>
#include <NTL/ZZ.h>
#include <iostream>
#include <chrono>
#include <cstdlib>

using namespace NTL;
using namespace std;

class Timer {
    using Clock = std::chrono::high_resolution_clock;
    Clock::time_point start_time;
public:
    Timer() : start_time(Clock::now()) {}
    double elapsed() {
        auto end_time = Clock::now();
        return std::chrono::duration<double>(end_time - start_time).count();
    }
};

int main(int argc, char** argv) {
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " <p> <e>" << endl;
        return 1;
    }

    long p_val = atol(argv[1]);
    long e_val = atol(argv[2]);

    cout << "=== NTL Benchmark (The Standard Approach) ===" << endl;
    cout << "Target: p=" << p_val << ", e=" << e_val << endl;

    // --- 关键修正 ---
    // NTL 的 CanZass 只能在域 (Field) 上工作。
    // 如果 e > 1，直接初始化 ZZ_p(p^e) 会导致算法崩溃。
    // 为了公平对比，我们让 NTL 执行 "Step 1: Base Factorization" (这是标准 Hensel Lifting 的第一步)
    // 我们记录这一步的时间，作为 "Standard Method" 的最低起步价。
    
    if (e_val > 1) {
        cout << "[WARNING] NTL native factorization strictly requires a Field." << endl;
        cout << "[INFO] Downgrading modulus to p (e=1) to measure Base Factorization time." << endl;
        cout << "[INFO] Real Lifting time would be significantly higher (polynomial arithmetic)." << endl;
    }

    // 1. 即使 e > 1，我们也只初始化模数 p (Field)
    ZZ p = to_ZZ(p_val);
    ZZ_p::init(p); 

    // 2. 构建多项式 f = x^(p+1) - 1
    ZZ_pX f;
    SetCoeff(f, p_val + 1, 1); 
    SetCoeff(f, 0, -1);        

    cout << "Polynomial constructed (over F_p). Starting CanZass..." << endl;

    Timer t;
    
    Vec< Pair< ZZ_pX, long > > factors;
    CanZass(factors, f); // 这是一个 O(p^2) 级别的操作

    double duration = t.elapsed();

    long total_factors = 0;
    for (long i = 0; i < factors.length(); i++) {
        total_factors += factors[i].b;
        
        cout << factors[i].a << endl; 
    }

    cout << "---------------------------------" << endl;
    cout << "Total Factors Found (Base Layer): " << total_factors << endl;
    cout << "Time Elapsed                    : " << duration << " s" << endl;
    cout << "=================================" << endl;

    return 0;
}
