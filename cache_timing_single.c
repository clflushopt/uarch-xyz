#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <x86intrin.h>
#include <string.h>
#include <assert.h>

#define BUFFER_SIZE 8

// Number of experiments to run.
#define N 1000

// Metrology helpers.
uint64_t max(uint64_t* arr, size_t len) {
    assert(len > 0);
    uint64_t max = arr[0];

    for (int i = 0;i < len;i++) {
        if (arr[i] >= max) {
            max = arr[i];
        }
    }

    return max;
}

uint64_t min(uint64_t* arr, size_t len) {
    assert(len > 0);
    uint64_t min = arr[0];

    for (int i = 0;i < len;i++) {
        if (arr[i] <= min) {
            min = arr[i];
        }
    }

    return min;
}

uint64_t avg(uint64_t* arr, size_t len) {
    uint64_t avg = 0.;

    for (int i = 0;i < len;i++) {
        avg += arr[i];
    }

    return avg / len;
}

// Data buffer used for experiments.
char buffer[BUFFER_SIZE];

int main(int argc, char** argv) {
    uint64_t start, end;
    uint64_t timings[N];

    // Zero out the timings buffer.
    memset(timings, 0, sizeof(timings));

    // Zero out the data buffer.
    memset(buffer, 0, sizeof(buffer));

    // Initial flush to ensure we are in a known state.
    _mm_clflush(buffer);
    _mm_mfence();


    for (int i = 0; i < N;i++) {
        _mm_clflush(buffer);
        _mm_mfence();

        start = __rdtsc();

        volatile uint64_t x = buffer[((buffer[0] + 4) ^ 1) ^1];
        _mm_mfence();

        end = __rdtsc();

        timings[i] = end - start;

        x += buffer[((buffer[0] + 4) ^ 1) ^1];
        _mm_mfence();
    }

    // Compute average, min, max accesses.
    uint64_t min_time = min(timings, N);
    uint64_t max_time = max(timings, N);
    uint64_t  avg_time = avg(timings, N);

    printf("Recorded access timings : \n");
    printf("Max access took: %ld cycles\n", max_time);
    printf("Min access took: %ld cycles\n", min_time);
    printf("Average access was: %ld cycles\n", avg_time);
}
