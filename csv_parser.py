import re
import csv
import pandas as pd
import matplotlib.pyplot as plt

def parse_log_file(log_path, output_csv):
    with open(log_path, 'r') as f:
        lines = f.readlines()

    generations = []
    current_gen = None
    in_species_section = False

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # Detect generation start
        match_gen = re.match(r"\*\*\*\*\*\* Running generation (\d+) \*\*\*\*\*\*", line)
        if match_gen:
            if current_gen:
                generations.append(current_gen)
            current_gen = {
                'generation': int(match_gen.group(1)),
                'species': []
            }
            in_species_section = False
            continue

        if not current_gen:
            continue

        # Extract metrics
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

    # Write main generation metrics CSV
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

    print(f"✅ Parsed {len(generations)} generations to {output_csv}")

    # Optional: Save species data
    species_csv = 'species_data.csv'
    with open(species_csv, 'w', newline='') as csvfile:
        fieldnames = ['generation', 'id', 'age', 'size', 'fitness', 'adj_fit', 'stag']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for gen in generations:
            for s in gen['species']:
                writer.writerow({
                    'generation': gen['generation'],
                    **s
                })
    print(f"✅ Species data saved to {species_csv}")

def plot_metrics(csv_path):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(10, 6))
    plt.plot(df["generation"], df["best_fitness"], label="Best Fitness", marker='o')
    plt.plot(df["generation"], df["avg_fitness"], label="Average Fitness", marker='x')
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("NEAT Training Fitness Over Generations")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    log_file = "logs.txt"  # your log file path
    gen_csv = "generation_stats.csv"
    parse_log_file(log_file, gen_csv)
    plot_metrics(gen_csv)
