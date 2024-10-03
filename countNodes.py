import json

def count_node_labels(json_file):
    # Load the JSON data from the file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Initialize a dictionary to hold the label counts
    label_count = {}
    total_nodes = 0
    # Iterate over each node in the JSON structure
    for entry in data:
        for node in entry['nodes']:
            # Get the labels for the current node
            total_nodes += 1
            labels = node.get('labels', [])
            for label in labels:
                # Increment the count for the label
                if label in label_count:
                    label_count[label] += 1
                else:
                    label_count[label] = 1

    print(total_nodes)
    # Print the label counts
    for label, count in label_count.items():
        print(f"{label}: {count}")

# Example usage
json_file_path = 'doraKnowledgeGraph.json'  # Replace with your JSON file path
count_node_labels(json_file_path)
