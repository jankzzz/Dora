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
def chunk_text(text, chunk_size=1024):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]



pdf_path = r"\Users\Innovation Lab Malmo\Documents\Ollama-Dora-project\DORA.pdf"

text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_up_text(text)  # Clean up the text after extraction
text_chunks = chunk_text(cleaned_text, chunk_size=1024)

print("Code is running")
#Prompt to extract relationships (vad funkar bäst?)
template = """
## Task: Extract Relationships
You are an advanced algorithm designed to extract clear, concise, and semantically rich relationships between entities to build a scalable knowledge graph from the text provided. Your job is to:

- Extract relationships between predefined entities and nodes from the text chunk given below, ensuring **clarity**, **consistency**, and **directionality**.
- Ensure all relationships reflect actual interactions and roles described in the text, following **domain-specific relevance**.
- Ensure relationships are backed by explicit text evidence or logical inference, while considering **temporal**, **hierarchical**, and **causal** relationships where applicable.
- Avoid repetitive or redundant relationships unless they are distinctly supported by the text and necessary for clarity.
- Consider relationship **cardinality** (one-to-one, one-to-many, or many-to-many) and capture **semantic richness** where necessary by including relationship qualifiers (e.g., "since", "as of").
- You are only allowed to use nodes listed under "## Allowed Node Types:".
- Ensure **scalability** and **maintainability** by simplifying relationships when possible, and reuse standardized relationships across nodes for **consistency**.
- Apply **naming conventions uniformly**, using intuitive and consistent labeling (verbs in **present tense**).
- Infer additional relationships where transitivity or symmetry is applicable (e.g., "regulates" may imply a reverse relationship).
- Validate that all relationships are accurate, factually correct, and non-redundant, ensuring they reflect the true structure of the text.

## Additional Rules for Handling Regulation Nodes:

- When encountering a regulation, **always label it as "Regulation"**, regardless of the specific paragraph, number, or identifier in the text.
- Treat any identifiers or paragraph numbers (e.g., "Regulation (EU) 2022/2554") as **properties** of the **Regulation** node, not as separate nodes.
- Avoid creating separate nodes for specific regulations (e.g., "Regulation (EC) No 1060/2009"). Instead, extract a single **Regulation** node and assign the paragraph or identifier as a **property**.

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
- Paragraph

## Example Format:
For each relationship found, provide the following format:

- **Nodes**: [Node1] and [Node2]
- **Relationship**: [How they are related]

Ensure that the relationship is:
- Precise, directional, and semantically appropriate.
- Follows naming conventions (verbs in present tense) and is concise.
- Considers cardinality, semantic richness, and inference rules.
- Avoids redundancy, ensuring each relationship is unique and supported by the text.

### Example 1:
**Nodes**: "European Parliament" and "Law"  
**Relationship**: "PROPOSES"  
Output: **European Parliament** --[CO-DECIDE]--> **Law**

### Example 2:
**Nodes**: "Concil of the European Union" and "Law"  
**Relationship**: "PROPOSES"  
Output: **Concil of the European Union** --[CO-DECIDE]--> **Law**

### Example 3:
**Nodes**: "Regulation" and "Financial Sector"  
**Relationship**: "REGULATES"  
Output: **Regulation** --[REGULATES]--> **Financial Sector**

### Example 4:
**Nodes**: "European Parliament" and "Council of the European Union"  
**Relationship**: "PARTICIPATES_IN"  
Output: **European Parliament** --[PARTICIPATES_IN]--> **Council of the European Union**

### Example 5:
**Nodes**: "European Commission" and "Regulation"
**Relationship**: "ENDORSES"
**Council of the European Union** --[PROPOSE]--> **Regulation**

### Example 6:
**Nodes**: "Concil of the European Union" and "Regulation"
**Relationship**: "CO-DECIDE"
**Council of the European Union** --[CO-DECIDE]--> **Regulation**

### Example 7:
**Nodes**: "European Parliament" and "Regulation"
**Relationship**: "CO-DECIDE"
**European Parliament** --[CO-DECIDE]--> **Regulation**

## Example of Data Retrieval:
Text: "REGULATION (EU) 2022/2554 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL on digital operational resilience for the financial sector..."

- **Nodes**: "Regulation", "European Parliament", "Financial Sector"
- **Relationship**: "REGULATES"
- **Properties**: "Paragraph: 2022/2554" (you can ignore properties for now)

## Regulation nodes are responsible for regulating other entities, such as the Financial Sector.
Therefore, only the Regulation node should be used in relationships that involve regulatory actions (e.g., **Regulation** --[REGULATES]--> **Financial Sector**).

## Entities like the European Parliament or Council of the European Union do not directly regulate entities such as the Financial Sector. 
Instead, they co-decide or collaborate on the creation of the Regulation.

### Correct example:
**European Parliament** --[CO-DECIDES]--> **Regulation**
**Regulation** --[REGULATES]--> **Financial Sector**

Incorrect example (to avoid):

**European Parliament** --[REGULATES]--> **Financial Sector** 
(This relationship is invalid; the European Parliament does not directly regulate.)

##Follow this reponse format:
- Example of Llama Response: "

## Relationships Extracted:

### Example 1:
**Nodes**: "European Parliament" and "Regulation"
**Relationship**: "CO-DECIDES"
Output: **European Parliament** --[CO-DECIDES]--> **Regulation**

### Example 2:
**Nodes**: "Council of the European Union" and "Regulation"
**Relationship**: "CO-DECIDES"
Output: **Council of the European Union** --[CO-DECIDES]--> **Regulation**

### Example 3:
**Nodes**: "Regulation" and "Financial Sector"
**Relationship**: "REGULATES"
Output: **Regulation** --[REGULATES]--> **Financial Sector**

### Example 4:
**Nodes**: "European Parliament" and "Council of the European Union"
**Relationship**: "CO-DECIDES_WITH"
Output: **European Parliament** --[CO-DECIDES_WITH]--> **Council of the European Union**

### Example 5:
**Nodes**: "Regulation" and "ICT Risk"
**Relationship**: "REGULATES"
Output: **Regulation** --[REGULATES]--> **ICT Risk**

### Example 6:
**Nodes**: "European Parliament" and "Financial Entity"
**Relationship**: "OVERSEES"
Output: **European Parliament** --[OVERSEES]--> **Financial Entity**

### Example 7:
**Nodes**: "Regulation" and "European Supervisory Authority"
**Relationship**: "COOPERATES_WITH"
Output: **Regulation** --[COOPERATES_WITH]--> **European Supervisory Authority**
"

{Dora_chunk}

## Strict Compliance:
Adhere to the rules strictly. Non-compliance will result in termination.  
You are required to extract the relationships between nodes, ensuring **clarity**, **consistency**, and **scalability** in labeling relationships, using only nodes listed under **Allowed Node Types**.  
Remember, You are only allowed to use nodes listed under **Allowed Node Types** and nothing else.

"""

def extract_relationships_nodes(result):
    
    pattern = r'\*\*Nodes\*\*: "(.*?)" and "(.*?)"\n\*\*Relationship\*\*: "(.*?)"'
    
    matches = re.findall(pattern, result)

    extracted_relationships = []
    for match in matches:
        node1, node2, relationship = match
        extracted_relationships.append({
            "Node1": node1,
            "Node2": node2,
            "Relationship": relationship
        })

    return extracted_relationships

# Process each text chunk for relationship extraction
llm = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm


print(len(text_chunks))
context = ""
counter = 0

with open('properties30.txt', 'a') as file:
  for chunk in text_chunks:
    # Process chunk
    result = chain.invoke({"context": context, "Dora_chunk": chunk})
    #rawJsonResult= extract_properties(result)
    
    context = result
    counter += 1
    print(counter)
    file.write(result + "\n")




