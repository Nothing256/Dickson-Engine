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
    if (argc < 4) {
        cerr << "Usage: " << argv[0] << " <p> <e> <n>" << endl;
        return 1;
    }

    long p_val = atol(argv[1]);
    long e_val = atol(argv[2]);
    long n_val = atol(argv[3]);

    ZZ p = to_ZZ(p_val);
    ZZ_p::init(p); 

    ZZ_pX f;
    SetCoeff(f, n_val, 1); 
    SetCoeff(f, 0, -1);        

    Timer t;
    Vec< Pair< ZZ_pX, long > > factors;
    CanZass(factors, f); 

    double duration = t.elapsed();

    cout << "Time Elapsed : " << duration << endl;
    return 0;
}
