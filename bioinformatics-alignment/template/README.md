# Bioinformatics: Read Alignment (Cookbook)

Builds from LabPod's CPU-only `ghcr.io/labpod/scipy-jupyter:v1-py312` composite image plus
`samtools` and `bwa` (installed via `apt-get` - both are stable, long-standing Ubuntu
packages) - see `context/Dockerfile`. The base provides Python 3.12, JupyterLab, and the
common scientific Python stack without baking a container user.
The bundle prepares the unchanged definition by pulling the immutable prebuilt image; its
**approximate pull size is 300 MB**. The complete Dockerfile remains in the bundle for review,
customization, air-gapped fallback, and a local build when the definition is changed.

`notebooks/alignment-basics.ipynb` generates a small synthetic reference genome and simulated
reads in Python (no download needed), then shells out to `bwa` and `samtools` - the two most
standard command-line tools in short-read genomics - to align, sort, index, and inspect the
result.

**Note on verification**: the synthetic read/reference generation and FASTA/FASTQ format were
verified in development. The `bwa`/`samtools` commands themselves were **not run against real
installs** while writing this (neither tool was available in that environment) - they follow
extremely standard, long-stable CLI usage, but verify the alignment results yourself the first
time through.

After starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/bioinformatics-alignment/notebooks/alignment-basics.ipynb` in
JupyterLab.
