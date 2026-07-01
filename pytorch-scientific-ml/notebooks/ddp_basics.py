"""Multi-GPU basics: DistributedDataParallel (DDP).

Unlike the other files in this cookbook, this is a plain script, not a notebook - DDP
launches one process per GPU (via `torchrun`), and a single Jupyter kernel is one process.
Run it from a LabPod Terminal inside the workspace, not from a notebook cell.

    torchrun --nproc_per_node=<N> ddp_basics.py

`<N>` = however many GPUs your workspace was given (check LabPod's workspace settings - this
cookbook's environment doesn't require a GPU at all, but this specific script needs one or
more to be interesting; N=1 still runs correctly, just without any real parallelism to show).

What it demonstrates: DDP replicates your model on every GPU, gives each GPU a different
slice of data, and after every backward pass, transparently all-reduces (averages) gradients
across every replica - so despite training on *different* data per rank, every replica's
parameters stay in lockstep. The script proves this directly, by gathering every rank's final
parameters and checking they're identical.
"""

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def main():
    backend = "nccl" if torch.cuda.is_available() else "gloo"
    dist.init_process_group(backend=backend)
    rank = dist.get_rank()
    world_size = dist.get_world_size()

    if torch.cuda.is_available():
        device = torch.device("cuda", rank % torch.cuda.device_count())
        torch.cuda.set_device(device)
    else:
        device = torch.device("cpu")

    torch.manual_seed(0)  # same initial weights on every rank, before wrapping in DDP
    model = nn.Sequential(nn.Linear(8, 16), nn.ReLU(), nn.Linear(16, 2)).to(device)
    model = DDP(model, device_ids=[device.index] if device.type == "cuda" else None)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)

    # Each rank sees a DIFFERENT random data shard - simulating a sharded dataset, the normal
    # case where every GPU processes its own slice of a larger batch.
    torch.manual_seed(100 + rank)
    X = torch.randn(32, 8, device=device)
    y = torch.randint(0, 2, (32,), device=device)

    for step in range(200):
        opt.zero_grad()
        logits = model(X)
        loss = nn.functional.cross_entropy(logits, y)
        loss.backward()  # DDP all-reduces gradients across every rank here
        opt.step()
        if rank == 0 and step % 50 == 0:
            print(f"step {step:4d}  loss {loss.item():.4f}  (rank 0's local batch)")

    # Verify DDP actually did its job: despite different data per rank, gradient
    # all-reduce should have kept every rank's parameters identical.
    local_params = torch.cat([p.data.flatten() for p in model.parameters()])
    gathered = [torch.zeros_like(local_params) for _ in range(world_size)]
    dist.all_gather(gathered, local_params)

    if rank == 0:
        max_diff = max((gathered[0] - g).abs().max().item() for g in gathered[1:])
        print(f"\nworld_size={world_size}  backend={backend}")
        print(f"max parameter difference across ranks: {max_diff:.2e} (should be ~0)")

    dist.destroy_process_group()


if __name__ == "__main__":
    main()
