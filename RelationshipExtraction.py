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
## Task: Extract Relationships
You are an advanced algorithm designed to extract clear, concise, and semantically rich relationships between entities to build a scalable knowledge graph from the text provided. Your job is to:

- Extract relationships between predefined nodes from the text chunk given below, ensuring **clarity**, **consistency**, and **directionality**.
- Ensure all relationships reflect actual interactions and roles described in the text, following **domain-specific relevance**.
- Ensure relationships are backed by explicit text evidence or logical inference, while considering **temporal**, **hierarchical**, and **causal** relationships where applicable.
- Avoid repetitive or redundant relationships unless they are distinctly supported by the text and necessary for clarity.
- Consider relationship **cardinality** (one-to-one, one-to-many, or many-to-many) and capture **semantic richness** where necessary by including relationship qualifiers (e.g., "since", "as of").
- You are only allowed to use nodes listed under "## Allowed Nodes:".
- Ensure **scalability** and **maintainability** by simplifying relationships when possible, and reuse standardized relationships across nodes for **consistency**.
- Apply **naming conventions uniformly**, using intuitive and consistent labeling (verbs in **present tense**).
- Infer additional relationships where transitivity or symmetry is applicable (e.g., "regulates" may imply a reverse relationship).
- Validate that all relationships are accurate, factually correct, and non-redundant, ensuring they reflect the true structure of the text.

## Allowed nodes to create relations between, if there are any:
{nodes}
If "nodes" is empty, use your advanced algorithm design to extract your own nodes from the "Dora_chunk", but only if "nodes" are empty!

## Follow the json_data format:
- Do not include the prompt in your response, keep it concise.
- Here is the context: {context}
- Example of Llama Response (Follow this format): {response}

Dora_chunk to extract relations from: 
{Dora_chunk}

## Strict Compliance:
Adhere to the rules strictly. Non-compliance will result in termination.  
You are required to extract the relationships between nodes, ensuring **clarity**, **consistency**, and **scalability** in labeling relationships, using only nodes listed under **Allowed Node Types**.  
Remember, You are only allowed to use nodes listed under **Allowed Node Types** and nothing else.

"""

response = """,
    [
    {
        "nodes": [
            {
                "id": "1",
                "labels": [
                    "Regulation"
                ],
                "properties": {
                    "Number": "2022/2554",
                    "Title": "Digital Operational Resilience for the Financial Sector",
                    "Jurisdiction": "EU"
                }
            },
            {
                "id": "2",
                "labels": [
                    "Financial Sector"
                ],
                "properties": {
                    "Type": "ICT Risk"
                }
            },
            {
                "id": "3",
                "labels": [
                    "Competent Authority"
                ],
                "properties": {
                    "Name": "European Systemic Risk Board (ESRB)"
                }
            },
            {
                "id": "4",
                "labels": [
                    "Financial Transmission Channels"
                ]
            },
            {
                "id": "5",
                "labels": [
                    "Union's Financial System"
                ]
            }
        ],
        "relationships": [
            {
                "id": "r1",
                "type": "REGULATES",
                "startNode": "1",
                "endNode": "2",
                "properties": {
                    "since": "2022"
                }
            },
            {
                "id": "r2",
                "type": "MONITORED_BY",
                "startNode": "2",
                "endNode": "3",
                "properties": {
                    "since": "2023"
                }
            },
            {
                "id": "r3",
                "type": "VULNERABLE_TO",
                "startNode": "5",
                "endNode": "4",
                "properties": {}
            },
            {
                "id": "r4",
                "type": "EXPOSES",
                "startNode": "4",
                "endNode": "5",
                "properties": {}
            }
        ]
    }
"""


llm = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm



batch_size = 10  
test_txt_data = []
nAndrCleand_data = []

llm = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

print(len(text_chunks))
context = ""
counter = 0

with open('propertiesJson.json', 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
    nodes = json_data[0].get("nodes", [])

with open('relationshipsAndNodes.txt', 'a') as file:
    for counter in range(len(text_chunks)):
        chunk = text_chunks[counter]

        # Get the corresponding node or return an empty string if out of bounds
        node = nodes[counter] if counter < len(nodes) else ""

        result = chain.invoke({
            "context": context,
            "Dora_chunk": chunk,
            "response": response,
            "nodes": node  # Pass the node or empty string
        })

        context = result

        print(counter)

        file.write(result + "\n")




