import os
import matplotlib.pyplot as plt
import networkx as nx
from neat.graphs import feed_forward_layers
from neat.graphs import required_for_output

try:
    import graphviz
except ImportError:
    graphviz = None


def draw_net(config, genome, view=False, node_names=None, filename=None, node_colors=None, fmt='png'):
    """ Receives a genome and draws a neural network with optional node names. """
    if graphviz is None:
        print("Graphviz not installed, cannot visualize network.")
        return

    if filename is None:
        filename = 'network'

    dot = graphviz.Digraph(format=fmt)

    inputs = set()
    for i in range(config.genome_config.num_inputs):
        inputs.add(-i - 1)

    outputs = set(range(config.genome_config.num_outputs))

    # Determine which nodes are required
    required_nodes = required_for_output(config.genome_config.input_keys,
                                         config.genome_config.output_keys,
                                         genome.connections)

    layers = feed_forward_layers(config.genome_config.input_keys,
                                 config.genome_config.output_keys,
                                 genome.connections)

    for n in required_nodes:
        if n in inputs:
            color = 'lightblue' if node_colors is None else node_colors.get(n, 'lightblue')
            name = node_names.get(n, str(n)) if node_names else str(n)
            dot.node(str(n), name, shape='box', style='filled', fillcolor=color)
        elif n in outputs:
            color = 'lightgreen' if node_colors is None else node_colors.get(n, 'lightgreen')
            name = node_names.get(n, str(n)) if node_names else str(n)
            dot.node(str(n), name, shape='ellipse', style='filled', fillcolor=color)
        else:
            color = 'lightgray' if node_colors is None else node_colors.get(n, 'lightgray')
            name = node_names.get(n, str(n)) if node_names else str(n)
            dot.node(str(n), name, shape='circle', style='filled', fillcolor=color)

    for cg in genome.connections.values():
        if cg.enabled:
            style = 'solid'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(abs(cg.weight / 5.0))
            dot.edge(str(cg.key[0]), str(cg.key[1]), color=color, penwidth=width, style=style)

    dot.render(filename, view=view)


def plot_stats(statistics, ylog=False, view=False, filename='avg_fitness.svg'):
    """ Plots the population's average and best fitness. """
    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = statistics.get_fitness_mean()

    plt.figure(figsize=(10, 5))
    plt.plot(generation, avg_fitness, 'b-', label="average")
    plt.plot(generation, best_fitness, 'r-', label="best")
    plt.title("Fitness over Generations")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend()
    plt.savefig(filename)
    if view:
        plt.show()
    plt.close()


def plot_species(statistics, view=False, filename='speciation.svg'):
    """ Visualizes speciation throughout evolution. """
    species_sizes = statistics.get_species_sizes()

    plt.figure(figsize=(10, 5))
    for species_id, sizes in species_sizes.items():
        plt.plot(sizes, label="species {}".format(species_id))
    plt.title("Speciation")
    plt.xlabel("Generations")
    plt.ylabel("Size")
    plt.grid()
    plt.savefig(filename)
    if view:
        plt.show()
    plt.close()
