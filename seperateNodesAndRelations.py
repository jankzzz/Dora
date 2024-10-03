import json

def split_json(input_file, output_nodes_file, output_relationships_file):
    # Load the JSON data from the input file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Separate the nodes and relationships
    nodes = []
    relationships = []

    # Loop through each item in the data
    for item in data:
        if "nodes" in item:
            nodes.extend(item["nodes"])
        if "relationships" in item:
            relationships.extend(item["relationships"])

    # Save the nodes to a separate JSON file
    with open(output_nodes_file, 'w') as f:
        json.dump(nodes, f, indent=4)

    # Save the relationships to a separate JSON file
    with open(output_relationships_file, 'w') as f:
        json.dump(relationships, f, indent=4)

    print(f"Nodes and relationships successfully saved to {output_nodes_file} and {output_relationships_file}")

# Example usage:
input_file = 'doraKnowledgeGraph.json'
output_nodes_file = 'nodesV1.json'
output_relationships_file = 'relationshipsV1.json'

split_json(input_file, output_nodes_file, output_relationships_file)
