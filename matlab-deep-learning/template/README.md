# MATLAB Deep Learning (Cookbook)

MATLAB in the browser (MathWorks matlab-proxy) built from `mathworks/matlab-deep-learning`,
not the plain `mathworks/matlab` base LabPod's own built-in MATLAB template uses - this one
includes Deep Learning Toolbox, which the example here needs.

**License required before this is usable at all.** MATLAB needs a valid, activated license -
specifically covering Deep Learning Toolbox and Parallel Computing Toolbox - reached either via
a network license manager (`MLM_LICENSE_FILE=port@host`) or MathWorks online licensing. There's
no way around this; if your lab doesn't have such a license, this cookbook isn't usable, same as
LabPod's own built-in MATLAB template.

Build steps:
1. Import this bundle with **Build now** checked, or import with **Build later** and click
   **Build** from My templates. This is a real image build: it pulls the MathWorks base image and
   installs matlab-proxy.
2. Enable the template, create a workspace, configure your license (see MathWorks' own
   matlab-proxy / container licensing docs for exact steps - out of scope here).
3. Open the **MATLAB** app from LabPod's Apps page.

Get the example script:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/matlab-deep-learning/digit_classifier.m` in the MATLAB editor.

**Note on verification**: unlike every other cookbook in this repo, this example was **not run
against a real MATLAB installation** while writing it (no MATLAB license available in that
environment) - it follows MathWorks' own official `trainnet` documentation example closely
(the current API; the older `trainNetwork` is deprecated as of R2024a), but verify it yourself
the first time through.
