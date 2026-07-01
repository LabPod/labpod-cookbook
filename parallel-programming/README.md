# Parallel Programming: OpenMP, MPI, CUDA

The same simple problem (estimate pi by numerical integration, or add two vectors for CUDA),
solved three ways - one per major parallelism model in HPC: shared-memory threads (OpenMP),
distributed-memory processes (MPI), and GPU SIMT (CUDA).

Unlike the other cookbooks in this repo, **this one has no `template/` bundle of its own** -
it uses LabPod's existing built-in template, **"Parallel Programming (CUDA/MPI/OpenMP)"**
(`tmpl-parallel-dev`), which already ships GCC/gfortran/clang, OpenMP, OpenMPI, the CUDA
toolkit, and Nsight profilers, served through VS Code for the Web. That template is opt-in
(admin builds it, EULA acknowledgement required for the CUDA toolkit) - ask your admin to
enable it if it isn't available yet.

## How to use this cookbook

1. Ask your admin to build and enable the **Parallel Programming (CUDA/MPI/OpenMP)** template
   if it isn't already (`/admin/templates`).
2. Create a workspace from that template and open it - it's VS Code for the Web, not
   JupyterLab.
3. Open a terminal and clone this repo into `/work`, which persists across stop/start:
   ```bash
   git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
   cd /work/labpod-cookbook/parallel-programming
   ```
4. Each subfolder is self-contained - see its own README for build/run commands:
   - [`openmp/`](openmp/) - `pi_openmp.c`
   - [`mpi/`](mpi/) - `pi_mpi.c`
   - [`cuda/`](cuda/) - `vector_add.cu`

## Next steps

- Compare `openmp/pi_openmp.c` and `mpi/pi_mpi.c` side by side - same computation, same
  reduction idea, different parallelism model.
- Profile the CUDA example with `nsys profile ./vector_add` (Nsight Systems, included in the
  template).
- Combine models: MPI across nodes/processes, OpenMP within each process, CUDA within each
  GPU - the standard shape of large-scale HPC codes.
