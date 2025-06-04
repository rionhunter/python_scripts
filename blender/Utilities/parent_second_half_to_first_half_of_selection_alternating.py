import bpy

# Get the selected nodes
selected_nodes = bpy.context.selected_nodes

# Check if there are nodes selected
if selected_nodes:
    # Split the selected nodes into two groups (A and B)
    group_a = selected_nodes[:len(selected_nodes)//2]
    group_b = selected_nodes[len(selected_nodes)//2:]

    # Parent nodes from group B to group A in alternating order
    for i in range(len(group_a)):
        parent_node = group_a[i]
        child_node = group_b[i % len(group_b)]  # Use modulo to loop through group B
        
        # Ensure the nodes are in the same node tree
        if parent_node.id_data == child_node.id_data:
            parent_node.parent = child_node
