// The same pi estimation as ../openmp/pi_openmp.c, but split across
// separate processes (MPI "ranks") instead of threads within one process -
// MPI's model: many processes, each with its own memory, communicating
// explicitly. Each rank computes a partial sum over its own slice of the
// interval; MPI_Reduce combines every rank's partial sum into rank 0's
// total (like OpenMP's reduction(+:sum), but across process boundaries).
#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long long n = 100000000; // 100M sample intervals total, across all ranks
    double dx = 1.0 / (double)n;

    double t0 = MPI_Wtime();

    long long chunk = n / size;
    long long start = rank * chunk;
    long long end = (rank == size - 1) ? n : start + chunk; // last rank takes the remainder

    double local_sum = 0.0;
    for (long long i = start; i < end; i++) {
        double x = (i + 0.5) * dx;
        local_sum += 4.0 / (1.0 + x * x);
    }

    double total_sum = 0.0;
    MPI_Reduce(&local_sum, &total_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    double t1 = MPI_Wtime();

    if (rank == 0) {
        double pi = total_sum * dx;
        printf("pi estimate: %.8f\n", pi);
        printf("ranks:       %d\n", size);
        printf("time:        %.3fs\n", t1 - t0);
    }

    MPI_Finalize();
    return 0;
}
