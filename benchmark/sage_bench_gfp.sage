import sys
import time

if len(sys.argv) < 4:
    print('Usage: sage sage_bench_gfp.sage <p> <e> <n>')
    sys.exit(1)

p = int(sys.argv[1])
e = int(sys.argv[2])  # ignored for domain factoring
n = int(sys.argv[3])

R = GF(p)
S = PolynomialRing(R, 'x')
x = S.gen()
f = x**n - 1

start = time.time()
factors = f.factor()
elapsed = time.time() - start

print(f'Factor Count : {len(list(factors))}')
print(f'Time Elapsed : {elapsed:.6f}')
