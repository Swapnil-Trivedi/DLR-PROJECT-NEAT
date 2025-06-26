import os
import csv

def create_log_dir(base_dir='log', run_number=1):
    """Create a log directory for the run."""
    log_dir = os.path.join(base_dir, f'run-{run_number}-data')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def init_csv_log(log_dir, filename='training_stats.csv'):
    """Initialize CSV log file with headers."""
    csv_path = os.path.join(log_dir, filename)
    csvfile = open(csv_path, mode='w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['Generation', 'BestFitness', 'AverageFitness', 'NumSpecies', 'BestGenomeID'])
    return csvfile, writer

def log_generation(writer, generation, best_fitness, avg_fitness, num_species, best_genome_id):
    """Write a generation's stats into the CSV."""
    writer.writerow([generation, best_fitness, avg_fitness, num_species, best_genome_id])

def close_csv_log(csvfile):
    """Close the CSV file handle."""
    csvfile.close()

def get_next_run_number(log_root='log'):
    """Auto-increment run number based on existing logs."""
    if not os.path.exists(log_root):
        return 1
    runs = [d for d in os.listdir(log_root) if d.startswith('run-') and os.path.isdir(os.path.join(log_root, d))]
    numbers = [int(d.split('-')[1]) for d in runs if d.split('-')[1].isdigit()]
    return max(numbers, default=0) + 1
