# Bioinformatics: Read Alignment (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `samtools` and `bwa` (installed
via `apt-get` - both are stable, long-standing Ubuntu packages) - see `context/Dockerfile`.
This has a real build step: after importing, click **Build** before creating a workspace.

`notebooks/alignment-basics.ipynb` generates a small synthetic reference genome and simulated
reads in Python (no download needed), then shells out to `bwa` and `samtools` - the two most
standard command-line tools in short-read genomics - to align, sort, index, and inspect the
result.

**Note on verification**: the synthetic read/reference generation and FASTA/FASTQ format were
verified in development. The `bwa`/`samtools` commands themselves were **not run against real
installs** while writing this (neither tool was available in that environment) - they follow
extremely standard, long-stable CLI usage, but verify the alignment results yourself the first
time through.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/bioinformatics-alignment/notebooks/alignment-basics.ipynb` in
JupyterLab.
