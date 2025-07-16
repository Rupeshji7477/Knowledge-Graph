import os
import asyncio
from neo4j import GraphDatabase
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from src.llm_extractor.extractor import extract_fragments_from_text
from src.knowledge_graph.populator import GraphPopulator

async def run_ingestion_pipeline():
    """Orchestrates the data ingestion pipeline."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    populator = GraphPopulator(driver)

    data_path = 'rules_data'
    
    print("Starting ingestion pipeline with LangChain...")
    for filename in os.listdir(data_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_path, filename)
            with open(file_path, 'r') as f:
                rule_text = f.read()
            
            extracted_data = await extract_fragments_from_text(rule_text)
            
            if extracted_data:
                populator.populate(extracted_data)
            else:
                print(f"Skipping population for {filename} due to extraction error.")

    driver.close()
    print("Ingestion pipeline finished.")

if __name__ == "__main__":
    asyncio.run(run_ingestion_pipeline())