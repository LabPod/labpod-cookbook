# CUDA: GPU (SIMT) parallelism

Adds two ~1M-element vectors on the GPU. Where OpenMP parallelizes across a handful of CPU
threads and MPI across a handful of processes, CUDA parallelizes across thousands of
lightweight GPU threads at once - `vector_add`'s kernel body runs once per output element,
launched as a grid of thread blocks.

```bash
nvcc -O2 vector_add.cu -o vector_add
./vector_add
```

Expected output: `PASS: all 1048576 elements correct`.

Unlike the OpenMP and MPI examples in this cookbook, this file was **not run against a real
GPU during development** (no CUDA-capable host was available while writing it) - it follows
NVIDIA's standard vector-add pattern closely, but verify it yourself the first time you run
it, and open an issue if something's off.
