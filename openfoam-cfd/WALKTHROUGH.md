# OpenFOAM CFD walkthrough: lid-driven cavity flow

OpenFOAM's own "hello world" tutorial: incompressible laminar flow in a 2D box with a moving
lid, solved with `icoFoam`. This case ships inside the `opencfd/openfoam-default` image itself
- we run OpenFOAM's own example, not a custom one, to keep this as low-risk as possible.

## 1. Confirm the environment is set up

```bash
icoFoam -help
```

If that fails with "command not found," the OpenFOAM environment variables (`FOAM_TUTORIALS`,
`PATH`, etc.) may need to be sourced first - look for and source the install's `etc/bashrc`:

```bash
ls /opt/openfoam*/etc/bashrc   # find the exact path for this image's OpenFOAM version
source /opt/openfoam*/etc/bashrc
```

## 2. Copy the tutorial case

Never edit tutorial cases in place - copy to a working directory under `/work` (persistent):

```bash
mkdir -p /work/openfoam-runs
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity /work/openfoam-runs/cavity
cd /work/openfoam-runs/cavity
```

## 3. Generate the mesh

```bash
blockMesh
checkMesh
```

`checkMesh` should report no errors - if it does, something about the copy went wrong.

## 4. Run the solver

```bash
icoFoam | tee icoFoam.log
```

Watch the residuals in the output - for this case they should decrease steadily as the
simulation advances through its time steps. When it finishes, confirm convergence:

```bash
tail -30 icoFoam.log
```

## 5. Look at the results

`paraFoam` (ParaView) is included in the image, but its GUI needs a display - not something
this container has out of the box. For a first pass without extra setup, check the raw output
data instead:

```bash
ls   # numbered time-step directories (0, 0.1, 0.2, ...) hold the solution fields
cat 0.5/U   # velocity field at t=0.5, as plain text
```

To actually visualize the flow, either export to a format you can open locally
(`foamToVTK`, then copy the `VTK/` directory out via LabPod's file browser and open it in a
local ParaView/VTK viewer), or set up VNC/X11 forwarding to this workspace - out of scope for
this basic walkthrough.

## Next steps

- Try another tutorial under `$FOAM_TUTORIALS` - `incompressible/simpleFoam/pitzDaily` (turbulent
  flow) is a common second example.
- Change `cavity`'s `system/blockMeshDict` mesh resolution and re-run - watch how the runtime
  and (if you push it far enough) numerical stability change.
- Compare with `../parallel-programming/` - OpenFOAM cases can run under MPI too
  (`decomposePar`, `mpirun -np N icoFoam -parallel`, `reconstructPar`) for larger meshes.
