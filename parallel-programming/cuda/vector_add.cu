// CUDA's canonical "hello world": add two vectors on the GPU. Unlike
// OpenMP/MPI, CUDA's parallelism model is SIMT (single instruction,
// multiple threads) across thousands of lightweight GPU threads, grouped
// into blocks. Each thread here computes exactly one output element.
#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define CUDA_CHECK(call)                                                       \
    do {                                                                       \
        cudaError_t err = (call);                                               \
        if (err != cudaSuccess) {                                               \
            fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__,   \
                    cudaGetErrorString(err));                                  \
            status = 1;                                                        \
            goto cleanup;                                                      \
        }                                                                      \
    } while (0)

__global__ void vector_add(const float *a, const float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main(void) {
    int n = 1 << 20; // ~1M elements
    size_t bytes = (size_t)n * sizeof(float);
    int threads_per_block = 256;
    int blocks = (n + threads_per_block - 1) / threads_per_block;
    int status = 0;
    int errors = 0;

    float *h_a = (float *)malloc(bytes);
    float *h_b = (float *)malloc(bytes);
    float *h_c = (float *)malloc(bytes);
    if (h_a == NULL || h_b == NULL || h_c == NULL) {
        fprintf(stderr, "host allocation failed\n");
        free(h_a);
        free(h_b);
        free(h_c);
        return 1;
    }
    for (int i = 0; i < n; i++) {
        h_a[i] = 1.0f;
        h_b[i] = 2.0f;
    }

    float *d_a = NULL, *d_b = NULL, *d_c = NULL;
    CUDA_CHECK(cudaMalloc(&d_a, bytes));
    CUDA_CHECK(cudaMalloc(&d_b, bytes));
    CUDA_CHECK(cudaMalloc(&d_c, bytes));

    CUDA_CHECK(cudaMemcpy(d_a, h_a, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_b, h_b, bytes, cudaMemcpyHostToDevice));

    vector_add<<<blocks, threads_per_block>>>(d_a, d_b, d_c, n);
    CUDA_CHECK(cudaGetLastError());

    CUDA_CHECK(cudaMemcpy(h_c, d_c, bytes, cudaMemcpyDeviceToHost));

    for (int i = 0; i < n; i++) {
        if (h_c[i] != 3.0f) {
            errors++;
        }
    }
    if (errors == 0) {
        printf("PASS: all %d elements correct\n", n);
    } else {
        printf("FAIL: %d of %d elements wrong\n", errors, n);
        status = 1;
    }

cleanup:
    if (d_a != NULL) {
        cudaFree(d_a);
    }
    if (d_b != NULL) {
        cudaFree(d_b);
    }
    if (d_c != NULL) {
        cudaFree(d_c);
    }
    free(h_a);
    free(h_b);
    free(h_c);
    return status;
}
