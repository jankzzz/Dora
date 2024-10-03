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

# PDF path
pdf_path = r"\Users\Innovation Lab Malmo\Documents\Ollama-Dora-project\DORA.pdf"

# Extract and clean text
text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_up_text(text)
text_chunks = chunk_text(cleaned_text, chunk_size=4096)

# New prompt to extract properties
template = """
## Task: Extract Properties
You are an advanced algorithm designed to extract properties of predefined entities and nodes to build a scalable knowledge graph from the text provided in the "Dora_chunk". Your job is to:

- Extract properties of nodes from the text chunk given below, ensuring **clarity**, **consistency**, and **relevance**.
- Each node's properties should reflect its characteristics, including identifiers, attributes, or any relevant details mentioned in the text.
- Avoid redundancy in properties unless distinctly supported by the text.
- Use the node types listed under "Allowed Node Types" and only nodes listed under "Allowed node types"

## Allowed Node Types:
- Organization
- Law
- Document
- Regulation
- European Parliament
- Council of the European Union
- Financial Sector
- ICT Risk
- Cyber Threat
- ICT Incident
- Financial Entity
- ICT Service Provider
- European Supervisory Authority
- Competent Authority
- Member State

## Follow the json_data format:
- Do not include the prompt in your response, keep it concise and only respond with the nodes and properties.
- Keep track of the last id used from the context to increment it making sure every id is unique
- Here is the context: {context}
- Example of Llama Response: 
{json_data}

##Dora chunk to extract nodes and properties from:
{Dora_chunk}

## Strict Compliance:
Adhere to the rules strictly. Non-compliance will result in termination.  
Use only nodes listed under **Allowed Node Types**.
"""

json_data = """
{
  "nodes": [
    {
      "id": "1",
      "labels": ["Regulation"],
      "properties": {
        "Paragraph": "2022/2554",
        "Title": "Digital Operational Resilience",
        "Jurisdiction": "EU"
      }
    }
  ]
}
"""


# Process each text chunk for property extraction
llm = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

print(len(text_chunks))
context = ""
counter = 0

with open('properties30.txt', 'a') as file:
  for chunk in text_chunks:
    # Process chunk
    result = chain.invoke({"context": context, "Dora_chunk": chunk, "json_data": json_data})
    
    context = result
    counter += 1
    print(counter)
    file.write(result + "\n")


