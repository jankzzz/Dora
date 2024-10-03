from neo4j import GraphDatabase
import json

# Neo4j credentials
uri = "bolt://localhost:7687"
username = "neo4j"
password = "Doratest123"

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

# Function to extract and map relationship data from various formats
def extract_relationship_info(data):
    # Extract the relevant keys for startNode and endNode, and normalize relationship types
    start_node = data.get('startNode') or data.get('from') or data.get('source')
    end_node = data.get('endNode') or data.get('to') or data.get('target')

    # Use 'type' if present, otherwise fallback to 'label'
    rel_type = data.get('type') or data.get('label', "").replace(" ", "_").upper()  # Normalize type/label to uppercase with underscores
    
    # Handle missing or empty rel_type
    if not rel_type:
        raise ValueError(f"Invalid relationship type or label in data: {data}")

    properties = data.get('properties', {})  # Default to an empty dictionary if 'properties' is missing

    return {
        'start_node': start_node,
        'end_node': end_node,
        'rel_type': rel_type,
        'properties': properties
    }

# Function to create relationships between existing nodes
def create_relationship(tx, relationship):
    start_node_id = relationship['start_node']
    end_node_id = relationship['end_node']
    rel_type = relationship['rel_type']
    properties = relationship['properties']

    # Clean property keys
    clean_properties = clean_property_keys(properties)

    # Dynamically create property assignments for Cypher if there are properties
    if clean_properties:  # Only add properties if they exist
        prop_string = ", ".join([f"{key}: ${key}" for key in clean_properties.keys()])
        query = (
            f"MATCH (a {{id: $startNodeId}}), (b {{id: $endNodeId}}) "
            f"CREATE (a)-[r:`{rel_type}` {{{prop_string}}}]->(b) "
            f"RETURN r"
        )
    else:  # If no properties, just create the relationship without any properties
        query = (
            f"MATCH (a {{id: $startNodeId}}), (b {{id: $endNodeId}}) "
            f"CREATE (a)-[r:`{rel_type}`]->(b) "
            f"RETURN r"
        )
    
    # Run the query with the actual property values (if any)
    tx.run(query, startNodeId=start_node_id, endNodeId=end_node_id, **clean_properties)

# Main function to load the JSON data into Neo4j
def load_data_to_neo4j(file_path):
    count = 0
    json_data = load_json_data(file_path)  # Load the JSON data from the file
    with driver.session() as session:
        for data in json_data:
            count += 1
            print(f"Processing item {count}")

            try:
                # Extract relationship info
                relationship_info = extract_relationship_info(data)
                
                # Check if we have valid start_node, end_node, and rel_type before proceeding
                if relationship_info['start_node'] and relationship_info['end_node']:
                    session.execute_write(create_relationship, relationship_info)
                else:
                    print(f"Skipping invalid relationship data at item {count}: {data}")
            except ValueError as e:
                print(f"Error processing item {count}: {e}")

# Load the relationships data into Neo4j from a JSON file
file_path = 'unique_relationships.json'  # Replace with your JSON file path
load_data_to_neo4j(file_path)

# Close the driver connection
driver.close()
