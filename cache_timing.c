#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <x86intrin.h> // For __rdtsc() and _mm_clflush()
#include <time.h>

#define ARRAY_SIZE 1024*64  // 64 KB array
#define ITERATIONS 1000     // Number of measurements per address
#define STEP_SIZE 64        // Step size in bytes (typical cache line)

// Function to flush the cache line of a specific memory address
void flush(void *p) {
    _mm_clflush(p);
    _mm_mfence();  // Ensure the flush is complete
}

// Function to access memory and time the access
uint64_t access_and_time(void *p) {
    uint64_t start, end;

    _mm_mfence();  // Serialize previous operations
    start = __rdtsc();
    _mm_mfence();  // Ensure rdtsc is executed

    *(volatile char*)p;  // Access the memory (read)

    _mm_mfence();  // Ensure the memory read is complete
    end = __rdtsc();
    _mm_mfence();  // Ensure rdtsc is executed

    return end - start;
}

int main() {
    // Allocate memory for our experiment
    char *array = (char*)malloc(ARRAY_SIZE);
    if (!array) {
        perror("Failed to allocate memory");
        return 1;
    }

    // Initialize the array with some values
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = (char)i;
    }

    // Allocate memory for results
    uint64_t **results = (uint64_t**)malloc(ARRAY_SIZE/STEP_SIZE * sizeof(uint64_t*));
    for (int i = 0; i < ARRAY_SIZE/STEP_SIZE; i++) {
        results[i] = (uint64_t*)malloc(ITERATIONS * sizeof(uint64_t));
    }

    // Warmup - access all memory locations
    for (int i = 0; i < ARRAY_SIZE; i += STEP_SIZE) {
        *(volatile char*)(array + i);
    }

    // Main experiment loop
    printf("Running cache timing experiment...\n");
    for (int iter = 0; iter < ITERATIONS; iter++) {
        if (iter % 100 == 0) {
            printf("Iteration %d/%d\n", iter, ITERATIONS);
        }

        for (int i = 0; i < ARRAY_SIZE; i += STEP_SIZE) {
            // Flush cache for this address
            flush(array + i);

            // First access (uncached)
            uint64_t time = access_and_time(array + i);

            // Store the result
            results[i/STEP_SIZE][iter] = time;
        }
    }

    // Write results to file
    FILE *fp = fopen("cache_timing_results.csv", "w");
    if (!fp) {
        perror("Failed to open output file");
        return 1;
    }

    // Write header
    fprintf(fp, "Address");
    for (int iter = 0; iter < ITERATIONS; iter++) {
        fprintf(fp, ",Iter%d", iter);
    }
    fprintf(fp, "\n");

    // Write data
    for (int i = 0; i < ARRAY_SIZE/STEP_SIZE; i++) {
        fprintf(fp, "%d", i * STEP_SIZE);
        for (int iter = 0; iter < ITERATIONS; iter++) {
            fprintf(fp, ",%llu", (unsigned long long)results[i][iter]);
        }
        fprintf(fp, "\n");
    }

    fclose(fp);
    printf("Results written to cache_timing_results.csv\n");

    // Free memory
    for (int i = 0; i < ARRAY_SIZE/STEP_SIZE; i++) {
        free(results[i]);
    }
    free(results);
    free(array);

    return 0;
}
