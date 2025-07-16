
# Knowledge Graph with Neo4j Setup
## Rule Retrieval System using a Knowledge Graph and LLMs

This project implements a complete pipeline to:
1. Read unstructured business rules from text files.
2. Use a Large Language Model (via LangChain) to extract structured information.
3. Populate a Neo4j Knowledge Graph with the extracted data.
4. Provide two methods for rule retrieval:
    - A production-ready API for fast, deterministic rule lookup based on a payload.
    - An interactive script for asking natural language questions about the rules.
---
# Project Directory Setup and Introduction
```
Knowledge-Graph/
|
|-- rules_data/
|   |-- rule_01.txt
|   |-- rule_02_updated.txt
|   |-- rule_03.txt
|
|-- src/
|   |-- __init__.py
|   |-- api/
|   |   |-- __init__.py
|   |   |-- app.py
|   |
|   |-- knowledge_graph/
|   |   |-- __init__.py
|   |   |-- populator.py
|   |   |-- querier.py
|   |
|   |-- llm_extractor/
|   |   |-- __init__.py
|   |   |-- extractor.py
|   |
|   |-- config.py
|
|-- .env
|-- main_ingest.py
|-- query_for_humans.py
|-- requirements.txt
|-- README.md
```

### **Setup Instructions**

**1. Prerequisites:**
   - Python 3.8+
   - Docker and Docker Compose
   - A Google AI API Key for the Gemini model. Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

**2. Clone and Install Dependencies:**
   ```bash
   git clone https://github.com/Rupeshji7477/Knowledge-Graph.git
   cd rule-kg-project
   pip install -r requirements.txt