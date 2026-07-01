# GROMACS Molecular Dynamics (Cookbook)

Pulls the official `gromacs/gromacs` image (CUDA-enabled build - works fine without a GPU too,
just slower), no custom build. Terminal-only, like `openfoam-cfd/` - you run `gmx` commands
directly through LabPod's Terminal, there's no web app here.

Unlike every other cookbook in this repo, **this one doesn't include a self-contained
tutorial**. GROMACS' official Docker image has no bundled "hello world" case the way OpenFOAM
does, and a real protein-in-water MD protocol is a long multi-step pipeline (structure prep,
solvation, ion addition, energy minimization, equilibration, production run) that's genuinely
easy to get subtly wrong without being able to test it end to end - which wasn't possible while
writing this (no GROMACS install available in that environment). Reproducing that risk here
didn't seem worth it when a much better resource already exists.

## What to actually do

1. Confirm the environment works:
   ```bash
   gmx --version
   gmx help commands
   ```
2. Follow **Justin Lemkul's "Protein-Ligand Complex" / lysozyme-in-water tutorial** -
   <http://www.mdtutorials.com/gmx/lysozyme/> - the de facto standard GROMACS tutorial that
   essentially every newcomer to the software uses, actively maintained, and far more
   thoroughly tested than anything written from scratch for this cookbook could be. It walks
   through the full pipeline: `pdb2gmx`, solvation, ion addition, energy minimization, NVT/NPT
   equilibration, and a production run.
3. Save your working files under `/work` (persistent across stop/start), not your home
   directory outside it.

## Next steps

- Compare CPU-only vs GPU-accelerated `mdrun` timing on the same system (`-nb gpu -pme gpu`
  flags) to see the GPU speedup directly.
- Once comfortable with the workflow, try `gmx insert-molecules` to build a much simpler
  system from scratch (e.g. a small Lennard-Jones liquid) instead of a full protein.
