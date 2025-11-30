def ordering_iter(start_block, ordered_blocks, traffic_data):
    visited = set()
    queue = [start_block]

    while queue:
        print("Queue", queue)
        current = queue.pop(0)
        print("calling while loop")

        if current in visited:
            continue
        visited.add(current)

        # Find children: (dst, src) means src -> dst
        for dst, src in traffic_data:
            print("calling for loop")
            if src == current and dst != src:   # skip self loops
                if dst not in ordered_blocks:
                    ordered_blocks.append(dst)
                queue.append(dst)

    return ordered_blocks


# Example
StartBlock = "A"
ordered_blocks = ["A"]
# Scenario 1
# traffic_data = [("B", "A"), ("B","B"), ("B","B"),("C", "B"), ("C","A"), ("D","C"), ("E","D")]

# Scenario 2
# traffic_data = [("C", "A"), ("B","B"), ("B","B"), ("B","A"), ("D","C"), ("E","D")]

traffic_data = [
    ("B","A"), ("B","B"), ("B","B"), ("B","B"),
    ("A","AA"), ("D","C"), ("C","A"), ("C","BB"),
    ("E","D"), ("F","E")
]

print(ordering_iter(StartBlock, ordered_blocks, traffic_data))
