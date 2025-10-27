import pandas as pd


li1 = [[1,2,3], [5,6,7]]

temp = [2, 1, 3]

if any(set(temp) == set(sublist) for sublist in li1):
    print("True")

else:
    print("False")




exit()
# Define nodes and edges
nodes = ['A', 'B', 'C', 'D', 'E']
edges = [('A', 'B'), ('B', 'E'), ('A', 'C'), ('C', 'E'), ('E', 'A'), ('A', 'D')]

# Initialize a square matrix of zeros
adj_matrix = pd.DataFrame(0, index=nodes, columns=nodes)

# Fill in the matrix based on edge directions
for u, v in edges:
    adj_matrix.loc[u, v] = 1     # direction u -> v
    adj_matrix.loc[v, u] = -1    # reverse direction v -> u

# print("Directed adjacency matrix (+1 forward, -1 reverse):\n")
# print(adj_matrix)


A_row = adj_matrix.loc['A']
ij_point = adj_matrix.iloc[1,1]


# DFS traversal
def traverse(matrix, nodes, start):
    visited = set()

    def dfs(current_index):
        current_node = nodes[current_index]
        print(f"Visiting {current_node}")
        visited.add(current_node)

        # Look across the entire row
        for j, value in adj_matrix.iloc[current_index]:
            print(j, value)
            exit()

            if value != 0:  # means there’s a connection
                next_node = nodes[j]
                direction = "→" if value == 1 else "←"
                print(f"  {current_node} {direction} {next_node}")

                # Visit next node if not already visited
                if next_node not in visited:
                    dfs(j)

    dfs(nodes.index(start))

traverse(adj_matrix, nodes, "A")
