import os
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt

def parse_log_file(log_path, output_csv, species_csv):
    with open(log_path, 'r') as f:
        lines = f.readlines()

    generations = []
    current_gen = None
    in_species_section = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        match_gen = re.match(r"\*\*\*\*\*\* Running generation (\d+) \*\*\*\*\*\*", line)
        if match_gen:
            if current_gen:
                generations.append(current_gen)
            current_gen = {'generation': int(match_gen.group(1)), 'species': []}
            in_species_section = False
            continue

        if not current_gen:
            continue

        if "Population's average fitness" in line:
            match = re.search(r"Population's average fitness:\s*([\d\.\-]+)\s*stdev:\s*([\d\.\-]+)", line)
            if match:
                current_gen['avg_fitness'] = float(match.group(1))
                current_gen['stdev_fitness'] = float(match.group(2))
        elif "Best fitness" in line:
            match = re.search(r"Best fitness:\s*([\d\.\-]+)", line)
            if match:
                current_gen['best_fitness'] = float(match.group(1))
        elif "Average adjusted fitness" in line:
            current_gen['avg_adjusted_fitness'] = float(line.split(":")[1])
        elif "Mean genetic distance" in line:
            match = re.search(r"Mean genetic distance\s*([\d\.\-]+),\s*standard deviation\s*([\d\.\-]+)", line)
            if match:
                current_gen['mean_genetic_distance'] = float(match.group(1))
                current_gen['std_genetic_distance'] = float(match.group(2))
        elif "Generation time" in line:
            match = re.search(r"Generation time:\s*([\d\.\-]+)", line)
            if match:
                current_gen['gen_time'] = float(match.group(1))
        elif "ID" in line and "stag" in line:
            in_species_section = True
            continue
        elif in_species_section:
            if "Total extinctions" in line:
                in_species_section = False
                continue
            parts = line.split()
            if len(parts) >= 6:
                species = {
                    'id': parts[0],
                    'age': parts[1],
                    'size': parts[2],
                    'fitness': parts[3],
                    'adj_fit': parts[4],
                    'stag': parts[5]
                }
                current_gen['species'].append(species)

    if current_gen:
        generations.append(current_gen)

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['generation', 'avg_fitness', 'stdev_fitness', 'best_fitness',
                      'avg_adjusted_fitness', 'mean_genetic_distance', 'std_genetic_distance', 'gen_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for gen in generations:
            writer.writerow({
                'generation': gen.get('generation'),
                'avg_fitness': gen.get('avg_fitness'),
                'stdev_fitness': gen.get('stdev_fitness'),
                'best_fitness': gen.get('best_fitness'),
                'avg_adjusted_fitness': gen.get('avg_adjusted_fitness'),
                'mean_genetic_distance': gen.get('mean_genetic_distance'),
                'std_genetic_distance': gen.get('std_genetic_distance'),
                'gen_time': gen.get('gen_time'),
            })

    with open(species_csv, 'w', newline='') as csvfile:
        fieldnames = ['generation', 'id', 'age', 'size', 'fitness', 'adj_fit', 'stag']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for gen in generations:
            for s in gen['species']:
                writer.writerow({'generation': gen['generation'], **s})


def plot_all(csv_path, species_csv, output_dir):
    import matplotlib.cm as cm
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    species_df = pd.read_csv(species_csv)
    species_df["size"] = pd.to_numeric(species_df["size"], errors='coerce')
    species_df.dropna(subset=["size"], inplace=True)

    num_gens = len(df)
    colors = cm.get_cmap('tab20', num_gens)

    # Plot 1: Fitness (simple line with generation-colored dots)
    plt.figure(figsize=(10, 5))
    plt.plot(df["generation"], df["best_fitness"], color='gray', linestyle='--', label="Best Fitness")
    plt.plot(df["generation"], df["avg_fitness"], color='black', linestyle='-', label="Average Fitness")
    for i in range(num_gens):
        plt.scatter(df["generation"][i], df["best_fitness"][i], color=colors(i), s=40)
        plt.scatter(df["generation"][i], df["avg_fitness"][i], color=colors(i), marker='x', s=40)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness per Generation")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fitness_simple.png")
    plt.close()

    # Plot 2: Genetic Distance
    plt.figure(figsize=(10, 5))
    plt.plot(df["generation"], df["mean_genetic_distance"], color='black', linestyle='-')
    for i in range(num_gens):
        plt.scatter(df["generation"][i], df["mean_genetic_distance"][i], color=colors(i), s=40)
    plt.xlabel("Generation")
    plt.ylabel("Mean Genetic Distance")
    plt.title("Genetic Distance per Generation")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/genetic_distance_simple.png")
    plt.close()

    # Plot 3: Generation Time
    plt.figure(figsize=(10, 5))
    plt.plot(df["generation"], df["gen_time"], color='black', linestyle='-')
    for i in range(num_gens):
        plt.scatter(df["generation"][i], df["gen_time"][i], color=colors(i), s=40)
    plt.xlabel("Generation")
    plt.ylabel("Generation Time (s)")
    plt.title("Generation Time per Generation")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/generation_time_simple.png")
    plt.close()

    # Plot 4: Species Sizes (stacked bars, clean)
    pivot = species_df.pivot_table(index="generation", columns="id", values="size", aggfunc="sum", fill_value=0)
    pivot.plot(kind='bar', stacked=True, figsize=(12, 5), colormap='tab20')
    plt.title("Species Size per Generation")
    plt.xlabel("Generation")
    plt.ylabel("Size")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/species_sizes_simple.png")
    plt.close()

    print(f"✅ Simple plots saved in: {output_dir}")


if __name__ == "__main__":
    log_file = "logs.txt"  # 🔁 Replace with your actual log filename
    gen_csv = "generation_stats.csv"
    species_csv = "species_data.csv"
    image_dir = "./images"

    parse_log_file(log_file, gen_csv, species_csv)
    plot_all(gen_csv, species_csv, image_dir)
