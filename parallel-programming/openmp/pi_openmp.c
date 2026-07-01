// Estimate pi via numerical integration of 4/(1+x^2) from 0 to 1, in
// parallel across threads with OpenMP. #pragma omp parallel for splits the
// loop's iterations across threads; reduction(+:sum) gives each thread its
// own private partial sum and safely combines them at the end (without it,
// every thread would race on the same `sum` variable).
#include <stdio.h>
#include <omp.h>

int main(void) {
    long long n = 100000000; // 100M sample intervals
    double dx = 1.0 / (double)n;
    double sum = 0.0;

    double t0 = omp_get_wtime();
    #pragma omp parallel for reduction(+:sum)
    for (long long i = 0; i < n; i++) {
        double x = (i + 0.5) * dx;
        sum += 4.0 / (1.0 + x * x);
    }
    double pi = sum * dx;
    double t1 = omp_get_wtime();

    printf("pi estimate: %.8f\n", pi);
    printf("threads:     %d\n", omp_get_max_threads());
    printf("time:        %.3fs\n", t1 - t0);
    return 0;
}
