from neo4j import GraphDatabase
import json  # Import the json module

# Neo4j credentials
uri = "neo4j+ssc://02fe2ba7.databases.neo4j.io:7687"
#"neo4j+s://02fe2ba7.databases.neo4j.io:7687"
username = "fredrik"
password = ""

# Create the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))
# Function to load JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to create nodes dynamically
def create_node(tx, node):
    labels = ":".join([label.replace(" ", "_") for label in node['labels']])
    properties = node.get('properties', {})
    node_id = node['id']  # Get the id for the node
    
    # Add the id property to the node
    properties['id'] = node_id

    # Dynamically create property assignments for Cypher if there are properties
    if properties:
        prop_string = ", ".join([f"{key}: ${key}" for key in properties.keys()])
        query = f"CREATE (n:`{labels}` {{{prop_string}}}) RETURN n"  # Use backticks for labels
    else:
        query = f"CREATE (n:`{labels}`) RETURN n"  # Handle nodes without properties
    
    # Run the query with the actual property values
    tx.run(query, **properties)

# Function to create relationships dynamically
def create_relationship(tx, relationship):
    # Determine the relationship format
    if 'startNode' in relationship and 'endNode' in relationship:
        start_node_id = relationship['startNode']
        end_node_id = relationship['endNode']
        rel_type = relationship.get('label') or relationship.get('type') or relationship.get('relationship')
    elif 'from' in relationship and 'to' in relationship:
        start_node_id = relationship['from']
        end_node_id = relationship['to']
        rel_type = relationship.get('label') or relationship.get('type') or relationship.get('relationship')
    elif 'source' in relationship and 'target' in relationship:
        start_node_id = relationship['source']
        end_node_id = relationship['target']
        rel_type = relationship.get('label') or relationship.get('type') or relationship.get('relationship')
    elif 'subject' in relationship and 'object' in relationship:
        start_node_id = relationship['subject']
        end_node_id = relationship['object']
        rel_type = relationship.get('label') or relationship.get('type') or relationship.get('relationship')
    else:
        raise ValueError("Invalid relationship format")
    
    properties = relationship.get('properties', {})

    # Log the relationship creation attempt
   # print(f"Checking for existing relationship: {rel_type.upper()} from {start_node_id} to {end_node_id} with properties {properties}")

    # Check if the relationship already exists
    query_check = f"""
    MATCH (a)-[r:`{rel_type.upper()}`]->(b)
    WHERE a.id = $start_node_id AND b.id = $end_node_id
    RETURN COUNT(r) AS relationship_exists
    """

    exists = tx.run(query_check, start_node_id=start_node_id, end_node_id=end_node_id).single().get("relationship_exists")

    if exists == 0:
        # Create the relationship if it does not exist
        query_create = f"""
        MATCH (a), (b)
        WHERE a.id = $start_node_id AND b.id = $end_node_id
        CREATE (a)-[r:`{rel_type.upper()}` {{{", ".join([f"{key}: ${key}" for key in properties.keys()])}}}]->(b)
        RETURN r
        """
        
        params = {"start_node_id": start_node_id, "end_node_id": end_node_id, **properties}
        
        # Run the query with the actual property values
        tx.run(query_create, **params)
       # print(f"Created relationship: {rel_type.upper()} from {start_node_id} to {end_node_id} with properties {properties}")
   # else:
    #    print(f"Relationship already exists: {rel_type.upper()} from {start_node_id} to {end_node_id}")

# Main function to load the JSON data into Neo4j
def load_data_to_neo4j(file_path):
    count =0
    json_data = load_json_data(file_path)  # Load the JSON data from the file
    try:
        with driver.session() as session:
            for data in json_data:
                count+=1
                print(count)
                # Create nodes
                for node in data['nodes']:
                    session.execute_write(create_node, node)
                #    Create relationships
                for relationship in data['relationships']:
                    session.execute_write(create_relationship, relationship)
        print("Connected successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
           
    

# Load the data into Neo4j from a JSON file
file_path = 'doraKnowledgeGraph.json'  # Replace with your JSON file path
load_data_to_neo4j(file_path)

# Close the driver connection
driver.close()
