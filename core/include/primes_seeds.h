#ifndef PRIMES_SEEDS_H
#define PRIMES_SEEDS_H

#include "poly_alg.h"

// Fetches a mathematically verified primitive seed polynomial for the given prime p and dimension m.
// Returns NULL if the prime is not precomputed in the dictionary.
Poly* get_precomputed_seed(poly_int p, int m);

#endif // PRIMES_SEEDS_H
