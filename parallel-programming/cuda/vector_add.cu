// CUDA's canonical "hello world": add two vectors on the GPU. Unlike
// OpenMP/MPI, CUDA's parallelism model is SIMT (single instruction,
// multiple threads) across thousands of lightweight GPU threads, grouped
// into blocks. Each thread here computes exactly one output element.
#include <stdio.h>
#include <cuda_runtime.h>

__global__ void vector_add(const float *a, const float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main(void) {
    int n = 1 << 20; // ~1M elements
    size_t bytes = (size_t)n * sizeof(float);

    float *h_a = (float *)malloc(bytes);
    float *h_b = (float *)malloc(bytes);
    float *h_c = (float *)malloc(bytes);
    for (int i = 0; i < n; i++) {
        h_a[i] = 1.0f;
        h_b[i] = 2.0f;
    }

    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, bytes);
    cudaMalloc(&d_b, bytes);
    cudaMalloc(&d_c, bytes);

    cudaMemcpy(d_a, h_a, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, bytes, cudaMemcpyHostToDevice);

    int threads_per_block = 256;
    int blocks = (n + threads_per_block - 1) / threads_per_block;
    vector_add<<<blocks, threads_per_block>>>(d_a, d_b, d_c, n);

    cudaMemcpy(h_c, d_c, bytes, cudaMemcpyDeviceToHost);

    int errors = 0;
    for (int i = 0; i < n; i++) {
        if (h_c[i] != 3.0f) {
            errors++;
        }
    }
    if (errors == 0) {
        printf("PASS: all %d elements correct\n", n);
    } else {
        printf("FAIL: %d of %d elements wrong\n", errors, n);
    }

    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    free(h_a);
    free(h_b);
    free(h_c);
    return 0;
}
