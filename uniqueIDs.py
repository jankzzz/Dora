import json

# Helper function to normalize relationship keys
def normalize_relationship(relationship):
    """
    Normalize the keys in the relationship to use 'startNode' and 'endNode'.
    Handles different variations like 'source'/'target', 'from'/'to', etc.
    """
    if 'startNode' in relationship and 'endNode' in relationship:
        return relationship  # Already in correct format
    elif 'source' in relationship and 'target' in relationship:
        relationship['startNode'] = relationship.pop('source')
        relationship['endNode'] = relationship.pop('target')
    elif 'from' in relationship and 'to' in relationship:
        relationship['startNode'] = relationship.pop('from')
        relationship['endNode'] = relationship.pop('to')
    
    return relationship

def assign_unique_ids(nodes, relationships, start_id):
    node_id_map = {}  # Map old node IDs to new ones
    new_nodes = []
    new_relationships = []
    
    # Assign new IDs to nodes
    for node in nodes:
        new_id = str(start_id)  # Generate a new unique ID
        node_id_map[node['id']] = new_id  # Map old ID to new ID
        node['id'] = new_id  # Replace old ID with new ID
        new_nodes.append(node)
        start_id += 1  # Increment the global ID counter
    
    # Normalize and update relationships with new node IDs
    for relationship in relationships:
        relationship = normalize_relationship(relationship)  # Normalize the relationship format
        relationship['startNode'] = node_id_map[relationship['startNode']]
        relationship['endNode'] = node_id_map[relationship['endNode']]
        new_relationships.append(relationship)

    return new_nodes, new_relationships, start_id

def process_files(nodes_file, relationships_file, output_nodes_file, output_relationships_file):
    with open(nodes_file, 'r') as f:
        nodes_data = json.load(f)
    
    with open(relationships_file, 'r') as f:
        relationships_data = json.load(f)

    start_id = 1  # Global ID counter for nodes

    # Generate unique IDs and update relationships
    new_nodes, new_relationships, start_id = assign_unique_ids(nodes_data, relationships_data, start_id)

    # Save nodes and relationships to separate files
    with open(output_nodes_file, 'w') as f:
        json.dump(new_nodes, f, indent=4)
    
    with open(output_relationships_file, 'w') as f:
        json.dump(new_relationships, f, indent=4)
    
    print(f"Processed files. Nodes saved to {output_nodes_file}, relationships saved to {output_relationships_file}")

# Example usage
nodes_file = 'nodesV1.json'  # Input file with nodes
relationships_file = 'relationshipsV2.json'  # Input file with relationships
output_nodes_file = 'unique_nodes.json'  # Output file for nodes with unique IDs
output_relationships_file = 'unique_relationships.json'  # Output file for relationships with updated IDs

process_files(nodes_file, relationships_file, output_nodes_file, output_relationships_file)
