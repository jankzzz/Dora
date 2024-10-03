from neo4j import GraphDatabase
import json

# Neo4j credentials
uri = "bolt://localhost:7687"
username = "neo4j"
password = "xxx"

# Create the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to load JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Helper function to clean property keys by replacing spaces and hyphens with underscores
def clean_property_keys(properties):
    # Replace spaces and hyphens with underscores in property keys
    return {key.replace(" ", "_").replace("-", "_"): value for key, value in properties.items()}

# Function to create nodes dynamically
def create_node(tx, node):
    labels = ":".join([label.replace(" ", "_") for label in node['labels']])  # Replace spaces in labels
    properties = node.get('properties', {})
    node_id = node['id']  # Get the id for the node
    
    # Add the id property to the node
    properties['id'] = node_id

    # Clean property keys (replace spaces and hyphens with underscores)
    clean_properties = clean_property_keys(properties)

    # Dynamically create property assignments for Cypher if there are properties
    if clean_properties:
        prop_string = ", ".join([f"{key}: ${key}" for key in clean_properties.keys()])
        query = f"CREATE (n:`{labels}` {{{prop_string}}}) RETURN n"  # Use backticks for labels
    else:
        query = f"CREATE (n:`{labels}`) RETURN n"  # Handle nodes without properties
    
    # Run the query with the actual property values
    tx.run(query, **clean_properties)


# Main function to load the JSON data into Neo4j
def load_data_to_neo4j(file_path):
    count = 0
    json_data = load_json_data(file_path)  # Load the JSON data from the file
    with driver.session() as session:
        for data in json_data:
            count += 1
            print(count)
            # Create nodes
            for node in data['nodes']:
                session.execute_write(create_node, node)

# Load the data into Neo4j from a JSON file
file_path = 'V2properties62-69.json'  # Replace with your JSON file path
load_data_to_neo4j(file_path)

# Close the driver connection
driver.close()
