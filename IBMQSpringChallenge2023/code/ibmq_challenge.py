from sherbrooke import sherbrooke_map, qubit_layout
import matplotlib.pyplot as plt
import colorsys
import numpy as np

height = 13
width = 15

def step_colormap(val, cmin, cmax):
    rgb_color = np.array(colorsys.hsv_to_rgb((val - cmin) / (cmax - cmin), 1.0, 1.0)) * 255
    return "#" + "".join(f"{int(c):02x}" for c in rgb_color)

def find_index_in_layout(qubit: int) -> tuple[int, int]:
    for i in range(height):
        for j in range(width):
            if qubit == qubit_layout[i][j]:
                return i, j
            
def plot_sherbrooke_map() -> None:
    plt.figure(figsize=(8.65, 7.50))
    
    for i in range(height):
        for j in range(width):
            qubit = qubit_layout[i][j]
            
            if qubit != -1:
                plt.scatter([j], [height-i-1], s=600, c="#c0c0e0")
                plt.annotate(str(qubit), (j, height-i-1), c="#303030", weight="bold", ha="center", va="center")
                
                for neighbour in sherbrooke_map[qubit]:
                    ni, nj = find_index_in_layout(neighbour)
                    plt.plot([j, nj], [height-i-1, height-ni-1], c=step_colormap(80, 0, 127), linewidth=4, zorder=-1)
        
    plt.axis((-1, width, -1, height))
    plt.xticks([], [])
    plt.yticks([], [])
    plt.tight_layout()
    plt.savefig("figures/sherbrooke_plot.png", dpi=300, bbox_inches="tight")

def draw_cmap_connections(cnot_connections: dict, steps: int) -> None:
    plt.figure(figsize=(8.65, 7.50))
    drawn_qubits = list()
    labeled_steps = list()
    
    for step, connections in cnot_connections.items():        
        for connection in connections:
            if step not in labeled_steps:
                labeled_steps.append(step)
                label = f"Step: {step}"
            else:
                label = ""
            
            qubit, neighbour = connection
            (iqub, jqub), (inei, jnei) = find_index_in_layout(qubit), find_index_in_layout(neighbour)
            plt.plot([jqub, jnei], [height-iqub-1, height-inei-1], c=step_colormap(step, 0, steps+2), label=label, linewidth=4, zorder=-1)
            
            if qubit not in drawn_qubits:
                drawn_qubits.append(qubit)
                plt.scatter([jqub], [height-iqub-1], s=600, c="#c0c0e0")
                plt.annotate(str(qubit), (jqub, height-iqub-1), c="#303030", weight="bold", ha="center", va="center")
            
            if neighbour not in drawn_qubits:
                drawn_qubits.append(neighbour)
                plt.scatter([jnei], [height-inei-1], s=600, c="#c0c0e0")
                plt.annotate(str(neighbour), (jnei, height-inei-1), c="#303030", weight="bold", ha="center", va="center")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.axis((-1, width, -1, height))
    plt.xticks([], [])
    plt.yticks([], [])
    plt.tight_layout()
    plt.savefig("figures/best_connection.png", dpi=300, bbox_inches="tight")
            
def traverse_map(start: int) -> tuple[list, int]:
    visited_qubits = list()
    cnot_connections = dict()
    current_qubits = [start]
    step_counter = 0

    visited_qubits.append(start)

    while len(visited_qubits) < 127:
        next_qubits = list()
        cnot_connections[step_counter] = list()
        
        for qubit in current_qubits:
            for neighbour in sherbrooke_map[qubit]:
                if neighbour not in visited_qubits:
                    visited_qubits.append(neighbour)
                    cnot_connections[step_counter].append((qubit, neighbour))
                    next_qubits.append(neighbour)
        
        step_counter += 1
        current_qubits = next_qubits
    
    return cnot_connections, step_counter

def best_traversal() -> None:
    best = 100, -1
    for start in range(127):
        _, steps = traverse_map(start)
        if steps < best[0]:
            best = steps, start
    
    cnot_connection, steps = traverse_map(best[1])
    print(f"Least amount of steps: {best[0]} with starting qubit: {best[1]}\n")
    print("CNOT connections for best starting point:")
    for step, connections in cnot_connection.items():
        print(f"Step: {step} | CNOT-connections: {connections}")
    
    draw_cmap_connections(cnot_connection, steps)

plot_sherbrooke_map()
best_traversal()
