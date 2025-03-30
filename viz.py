import csv
import os
import math

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

def mean(values):
    return sum(values) / len(values)

def median(values):
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_values[mid-1] + sorted_values[mid]) / 2
    else:
        return sorted_values[mid]

def std_dev(values):
    m = mean(values)
    squared_diff_sum = sum((x - m) ** 2 for x in values)
    return math.sqrt(squared_diff_sum / len(values))

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def find_potential_threshold(all_times):
    # Sort all times
    sorted_times = sorted(all_times)

    # Calculate differences between consecutive times
    differences = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times)-1)]

    # Find the index of the maximum difference
    max_diff_idx = differences.index(max(differences))

    # Calculate potential threshold
    return (sorted_times[max_diff_idx] + sorted_times[max_diff_idx+1]) / 2

def create_ascii_histogram(data, bins=20, width=60):
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / bins

    # Count values in each bin
    counts = [0] * bins
    for val in data:
        bin_idx = min(bins - 1, int((val - min_val) / bin_width))
        counts[bin_idx] += 1

    # Find the maximum count for scaling
    max_count = max(counts)
    scale = width / max_count

    # Create the histogram
    result = []
    result.append("Distribution of Access Times (ASCII Histogram)")
    result.append("-" * 60)

    for i in range(bins):
        bin_start = min_val + i * bin_width
        bin_end = bin_start + bin_width
        bar = "#" * int(counts[i] * scale)
        result.append(f"{bin_start:6.1f} - {bin_end:6.1f} | {bar} ({counts[i]})")

    result.append("-" * 60)
    result.append(f"Range: {min_val:.1f} to {max_val:.1f}, Bin width: {bin_width:.1f}")

    return "\n".join(result)

def main():
    filename = 'cache_timing_results.csv'
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return

    print(f"Reading data from {filename}...")
    addresses, timing_data = read_csv_file(filename)

    # Calculate statistics for all data
    all_times = flatten(timing_data)
    all_min = min(all_times)
    all_max = max(all_times)
    all_mean = mean(all_times)
    all_median = median(all_times)
    all_std = std_dev(all_times)

    # Calculate statistics for each address
    stats_by_address = []
    for i, addr in enumerate(addresses):
        times = timing_data[i]
        stats_by_address.append({
            'address': addr,
            'mean': mean(times),
            'median': median(times),
            'std_dev': std_dev(times),
            'min': min(times),
            'max': max(times)
        })

    # Find potential cache hit/miss threshold
    threshold = find_potential_threshold(all_times)

    # Create ASCII histogram
    hist = create_ascii_histogram(all_times)

    # Output to file
    with open('cache_timing_analysis.txt', 'w') as f:
        f.write("Cache Timing Analysis\n")
        f.write("====================\n\n")

        f.write("Overall Statistics:\n")
        f.write(f"  Min access time: {all_min} cycles\n")
        f.write(f"  Max access time: {all_max} cycles\n")
        f.write(f"  Mean access time: {all_mean:.2f} cycles\n")
        f.write(f"  Median access time: {all_median:.2f} cycles\n")
        f.write(f"  Std dev of access times: {all_std:.2f} cycles\n\n")

        f.write(f"Potential cache hit/miss threshold: {threshold:.2f} cycles\n")
        f.write(f"  Values below this are likely cache hits\n")
        f.write(f"  Values above this are likely cache misses\n\n")

        # Write the ASCII histogram
        f.write(hist)
        f.write("\n\n")

        # Write statistics for each address
        f.write("Statistics by Address:\n")
        f.write("Address,Mean,Median,StdDev,Min,Max\n")
        for stat in stats_by_address:
            f.write(f"{stat['address']},{stat['mean']:.2f},{stat['median']:.2f},{stat['std_dev']:.2f},{stat['min']},{stat['max']}\n")

    print(f"Analysis written to cache_timing_analysis.txt")
    print("Analysis complete!")

if __name__ == "__main__":
    main()
