# MPI: distributed-memory parallelism

The same pi estimation as `../openmp/pi_openmp.c`, split across separate MPI processes
("ranks") instead of threads - MPI's model: many processes, each with its own memory,
combining results by explicit message passing (`MPI_Reduce`) instead of a shared variable.

```bash
mpicc -O2 pi_mpi.c -o pi_mpi
mpirun -np 1 ./pi_mpi   # baseline
mpirun -np 4 ./pi_mpi   # compare - should be noticeably faster, same answer
```

Verified in development: both runs print the same `pi estimate: 3.14159265`, and 4 ranks
finished in about a quarter of the 1-rank time (0.129s -> 0.035s - your numbers depend on
core count).

This is the same computation as `../openmp/pi_openmp.c` on purpose - compare the two files
to see how the same parallel-reduction idea looks in each model.
