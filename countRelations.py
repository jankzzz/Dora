import json

def count_relationships(json_file):
    # Load the JSON data from the file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Initialize variables for total count and type count
    total_relationships = 0
    relationship_type_count = {}

    # Iterate over each entry in the JSON structure
    for entry in data:
        # Check if 'relationships' exist in the entry
        if 'relationships' in entry:
            relationships = entry['relationships']
            total_relationships += len(relationships)  # Count total number of relationships

            for relationship in relationships:
                # Identify type (could be 'type' or 'label', depending on format)
                rel_type = relationship.get('type') or relationship.get('label')

                if rel_type:
                    if rel_type in relationship_type_count:
                        relationship_type_count[rel_type] += 1
                    else:
                        relationship_type_count[rel_type] = 1

    # Print the total number of relationships
    print(f"Total Relationships: {total_relationships}")

    # Print the relationship type counts
    print("\nRelationship Type Counts:")
    for rel_type, count in relationship_type_count.items():
        print(f"{rel_type}: {count}")

    # Optionally return the counts if needed for further processing
    return total_relationships, relationship_type_count

# Example usage
json_file_path = 'doraKnowledgeGraph.json'  # Replace with your JSON file path
count_relationships(json_file_path)
