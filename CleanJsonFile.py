from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import PyPDF2
import re 
import json


# Step 1: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# Step 2: Clean up unnecessary spaces, line breaks, and hyphenations in the extracted text
def clean_up_text(text):
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)  # Remove unnecessary line breaks
    text = re.sub(r'-\n', '', text)  # Fix hyphenated words at line ends
    text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces to a single space
    text = re.sub(r'\s([?.!,"])', r'\1', text)  # Remove spaces before punctuation
    text = text.replace('“', '"').replace('”', '"')  # Handle smart quotes
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('—', '-')  # Replace em dashes with hyphens
    return text
 
# Step 3: Split text into chunks of 1024 characters
def chunk_text(text, chunk_size=4096):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


pdf_path = r"\Users\Innovation Lab Malmo\Documents\Ollama-Dora-project\DORA.pdf"

text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_up_text(text)  # Clean up the text after extraction
text_chunks = chunk_text(cleaned_text, chunk_size=4096)

print("Code is running")

template = """
Task: Process a JSON file containing nodes and relationships, ensuring data consistency, removing duplicates, and generating unique IDs.

Input: A JSON file with the following structure:

{JSON}

Output: Two separate JSON files:

nodes.json: Containing only the unique node objects.
relationships.json: Containing only the unique relationship objects, with start and end nodes referencing the corresponding IDs in nodes.json.

Instructions:

Parse the JSON file: Extract the nodes and relationships arrays.

Process nodes:
Create a set to store and or create unique node IDs.
Iterate over each node:
If the node's ID is already in the set, check if the label and properties are the same, if yes, remove the duplicate.
Otherwise, add the node's ID to the set.

Process relationships:
Create a set to store unique relationship IDs.
Iterate over each relationship:
If the relationship's ID is already in the set, check if the label and properties are the same, if yes, remove the duplicate.
Otherwise, add the relationship's ID to the set.
Ensure that the startNode and endNode IDs in the relationship correspond to existing node IDs.

Generate unique IDs:
For each node and relationship that remains, assign a unique numeric ID.
Update the startNode and endNode properties in relationships to reference the new IDs.
Output JSON files:
Write the processed nodes to nodes.json.
Write the processed relationships to relationships.json.

Here is the context:
{context}

Here is the nodes and relationships:
{nodes}
{relationships}

Create the output
"""

JSON = """
{
  "nodes": [
    // ... node objects ...
  ],
  "relationships": [
    // ... relationship objects ...
  ]
}
"""

llm = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

context = ""

with open('doraKnowledgeGraph.json', 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
    nodes = json_data[0].get("nodes", [])
    relationships = json_data[0].get("relationships", [])

with open('cleanJsonV1.txt', 'a') as file:
    for counter in range(len(nodes)):
        node = nodes[counter]
        relationship = relationships[counter]

        result = chain.invoke({
            "JSON": JSON,
            "context": context,
            "nodes": node,
            "relationships": relationship
        })

        context += result

        print(counter)

        file.write(result + "\n")




