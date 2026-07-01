# OpenMP: shared-memory parallelism

Estimates pi by numerical integration, split across CPU threads within a single process -
OpenMP's model: one process, multiple threads, shared memory.

```bash
gcc -O2 -fopenmp pi_openmp.c -o pi_openmp
OMP_NUM_THREADS=1 ./pi_openmp   # baseline
OMP_NUM_THREADS=8 ./pi_openmp   # compare - should be noticeably faster, same answer
```

Verified in development: both runs print the same `pi estimate: 3.14159265`, and 8 threads
finished in about a fifth of the 1-thread time (0.140s -> 0.030s on the machine this was
written on - your numbers depend on core count).

Compare with `../mpi/pi_mpi.c` - the exact same math problem, solved with a different
parallelism model (separate processes instead of threads).
