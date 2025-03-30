import csv
import matplotlib.pyplot as plt
import numpy as np
import os

# Check if matplotlib is available
try:
    import matplotlib
    has_matplotlib = True
except ImportError:
    has_matplotlib = False
    print("matplotlib not available. Will generate raw data analysis only.")

# Function to read the CSV file
def read_csv_file(filename):
    addresses = []
    timing_data = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        for row in reader:
            addresses.append(int(row[0]))
            # Convert timing values to integers
            times = [int(x) for x in row[1:]]
            timing_data.append(times)

    return addresses, timing_data

# Main function
def main():
    filename = 'cache_timing_results.csv'
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return

    print(f"Reading data from {filename}...")
    addresses, timing_data = read_csv_file(filename)

    # Convert to numpy array for easier calculations
    timing_matrix = np.array(timing_data)

    # Calculate statistics
    mean_times = np.mean(timing_matrix, axis=1)
    median_times = np.median(timing_matrix, axis=1)
    std_times = np.std(timing_matrix, axis=1)
    min_times = np.min(timing_matrix, axis=1)
    max_times = np.max(timing_matrix, axis=1)

    # Output basic statistics to text file
    with open('cache_timing_analysis.txt', 'w') as f:
        f.write("Cache Timing Analysis\n")
        f.write("====================\n\n")

        f.write("Overall Statistics:\n")
        f.write(f"  Min access time: {np.min(timing_matrix)} cycles\n")
        f.write(f"  Max access time: {np.max(timing_matrix)} cycles\n")
        f.write(f"  Mean access time: {np.mean(timing_matrix):.2f} cycles\n")
        f.write(f"  Median access time: {np.median(timing_matrix):.2f} cycles\n")
        f.write(f"  Std dev of access times: {np.std(timing_matrix):.2f} cycles\n\n")

        # Identify potential cache vs non-cache patterns
        # Simple approach: sort all times and look for a natural break
        all_times = timing_matrix.flatten()
        all_times.sort()

        # Calculate the differences between consecutive sorted times
        differences = [all_times[i+1] - all_times[i] for i in range(len(all_times)-1)]
        max_diff_idx = np.argmax(differences)
        potential_threshold = (all_times[max_diff_idx] + all_times[max_diff_idx+1]) / 2

        f.write(f"Potential cache hit/miss threshold: {potential_threshold:.2f} cycles\n")
        f.write(f"  Values below this are likely cache hits\n")
        f.write(f"  Values above this are likely cache misses\n\n")

        # Write statistics for each address
        f.write("Statistics by Address:\n")
        f.write("Address,Mean,Median,StdDev,Min,Max\n")
        for i, addr in enumerate(addresses):
            f.write(f"{addr},{mean_times[i]:.2f},{median_times[i]:.2f},{std_times[i]:.2f},{min_times[i]},{max_times[i]}\n")

    print(f"Basic statistics written to cache_timing_analysis.txt")

    # Create visualizations if matplotlib is available
    if has_matplotlib:
        # Create output directory if it doesn't exist
        if not os.path.exists('plots'):
            os.makedirs('plots')

        # Plot 1: Line plot of mean access times
        plt.figure(figsize=(10, 6))
        plt.plot(addresses, mean_times)
        plt.title('Mean Cache Access Times')
        plt.xlabel('Memory Address (offset in bytes)')
        plt.ylabel('Access Time (cycles)')
        plt.grid(True)
        plt.savefig('plots/mean_access_times.png')
        plt.close()

        # Plot 2: Histogram of all access times
        plt.figure(figsize=(10, 6))
        # Use log scale and remove extreme outliers
        flat_times = timing_matrix.flatten()
        q99 = np.percentile(flat_times, 99)  # 99th percentile
        filtered_times = flat_times[flat_times <= q99]  # Filter out extreme outliers
        plt.hist(filtered_times, bins=100)
        plt.title('Distribution of Access Times')
        plt.xlabel('Access Time (cycles)')
        plt.ylabel('Frequency')
        plt.yscale('log')  # Use log scale for y-axis to see small bars
        plt.grid(True)
        plt.savefig('plots/access_time_histogram.png')
        plt.close()

        # Plot 3: Min, mean, and max times by address
        plt.figure(figsize=(12, 6))
        plt.plot(addresses, min_times, 'g-', label='Min')
        plt.plot(addresses, mean_times, 'b-', label='Mean')
        plt.plot(addresses, max_times, 'r-', label='Max')

        max_iter = min(100, timing_matrix.shape[1])
        # Create a copy and apply log scaling for better visualization
        heatmap_data = timing_matrix[:, :max_iter].copy()
        # Add a small value to avoid log(0) issues
        heatmap_data = np.log1p(heatmap_data)

        plt.pcolormesh(np.arange(max_iter), addresses, heatmap_data, cmap='viridis')
        plt.colorbar(label='Log(Access Time + 1) (cycles)')
        plt.title('Access Times Heatmap - Log Scale (First 100 Iterations)')
        plt.xlabel('Iteration')
        plt.ylabel('Memory Address (offset in bytes)')
        plt.savefig('plots/access_times_heatmap_log.png')
        plt.close()

        # Add new plot: Scatter plot to better see patterns
        plt.figure(figsize=(12, 8))
        # Select a subset of data points for clarity
        sample_size = min(1000, timing_matrix.size)
        indices = np.random.choice(timing_matrix.size, sample_size, replace=False)
        y_indices, x_indices = np.unravel_index(indices, timing_matrix.shape)

        # Create scatter plot
        plt.scatter(x_indices, [addresses[i] for i in y_indices],
                   c=[timing_matrix[y,x] for y,x in zip(y_indices, x_indices)],
                   cmap='viridis', alpha=0.7, s=20)

        plt.colorbar(label='Access Time (cycles)')
        plt.title('Memory Access Times - Scatter Sample')
        plt.yscale('log')  # Log scale for y-axis to see patterns better
        plt.xlabel('Memory Address (offset in bytes)')
        plt.ylabel('Access Time (cycles)')
        plt.legend()
        plt.grid(True)
        plt.savefig('plots/min_mean_max_times.png')
        plt.close()

        # Plot 4: Simple heatmap-like visualization
        plt.figure(figsize=(12, 8))
        # Use pcolormesh for a heatmap-like visualization
        # Limit to first 100 iterations for visibility
        max_iter = min(100, timing_matrix.shape[1])
        plt.pcolormesh(np.arange(max_iter), addresses, timing_matrix[:, :max_iter])
        plt.colorbar(label='Access Time (cycles)')
        plt.title('Access Times Heatmap (First 100 Iterations)')
        plt.xlabel('Iteration')
        plt.ylabel('Memory Address (offset in bytes)')
        plt.savefig('plots/access_times_heatmap.png')
        plt.close()

        print(f"Visualizations created in the 'plots' directory")

    print("Analysis complete!")

if __name__ == "__main__":
    main()
