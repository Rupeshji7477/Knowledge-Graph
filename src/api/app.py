# from fastapi import FastAPI, HTTPException, Body
# from neo4j import GraphDatabase
# from typing import Dict, List
# from pydantic import BaseModel
# from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
# from src.knowledge_graph.querier import GraphQuerier

# app = FastAPI(
#     title="Rule Retrieval API",
#     description="An API to find business rules from a Knowledge Graph based on a given payload.",
#     version="1.0.0",
# )

# class FindRuleResponse(BaseModel):
#     best_matching_rule: str
#     all_matching_rules: List[str]


# try:
#     driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
#     querier = GraphQuerier(driver)
#     print("Successfully connected to Neo4j for API.")
# except Exception as e:
#     print(f"FATAL: Failed to connect to Neo4j. The API will not work. Error: {e}")
#     driver = None
#     querier = None


# # --- API Endpoint ---
# @app.post("/find_rule", response_model=FindRuleResponse)
# async def find_rule_endpoint(payload: Dict[str, str] = Body(
#     ...,
#     example={
#         "state": "Texas",
#         "property": "Residential",
#         "form": "form-tx-3"
#     }
# )):
#     """
#     Finds the most specific business rule that matches the criteria in the payload.

#     - **Receives**: A JSON object with key-value pairs representing rule conditions.
#     - **Returns**: The best matching rule and a list of all other applicable rules, sorted by specificity.
#     """
#     if not querier:
#         raise HTTPException(
#             status_code=503, 
#             detail="Service Unavailable: Database connection is not configured."
#         )

#     if not payload:
#         raise HTTPException(
#             status_code=400, 
#             detail="Bad Request: Payload cannot be empty."
#         )
    
#     try:
#         matching_rules = querier.find_rule(payload)
        
#         if not matching_rules:
#             raise HTTPException(
#                 status_code=404, 
#                 detail="No matching rule found for the given criteria."
#             )
            
#         return {
#             "best_matching_rule": matching_rules[0],
#             "all_matching_rules": matching_rules
#         }
#     except Exception as e:
#         print(f"An internal error occurred: {e}")
#         raise HTTPException(
#             status_code=500, 
#             detail=f"An internal server error occurred: {str(e)}"
#         )

# @app.get("/health")
# async def health_check():
#     """A simple endpoint to confirm the API is running."""
#     return {"status": "ok"}

from fastapi import FastAPI, HTTPException, Body
from neo4j import GraphDatabase
from typing import Dict, List, Union

from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from src.knowledge_graph.querier import GraphQuerier

app = FastAPI(
    title="Rule Composition API",
    description="An API to find and aggregate all applicable rule fragments from a Knowledge Graph.",
    version="2.0.0",
)

# --- Database Connection ---
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    querier = GraphQuerier(driver)
    print("Successfully connected to Neo4j for Rule Composition API.")
except Exception as e:
    print(f"FATAL: Failed to connect to Neo4j. Error: {e}")
    querier = None

# --- API Endpoint ---
@app.post("/compose_rule")
async def compose_rule_endpoint(payload: Dict[str, Union[str, List[str]]] = Body(
    ...,
    example={
        "state": "Florida",
        "property": "Golden",
        "form": ["03", "04"]
    }
)):
    """
    Finds all rule fragments matching the payload criteria and aggregates them.

    - **Receives**: A JSON object. Keys can have string or list-of-string values.
    - **Returns**: A single, combined rule string created from all found fragments.
    """
    if not querier:
        raise HTTPException(status_code=503, detail="Service Unavailable: DB connection failed.")

    try:
        # The querier now returns a list of content strings
        rule_fragments = querier.get_aggregated_rules(payload)
        
        if not rule_fragments:
            raise HTTPException(status_code=404, detail="No rule fragments found for the given criteria.")
            
        # Combine all the fragments into a single final rule text.
        final_rule = " ".join(rule_fragments)
        
        return {
            "composed_rule": final_rule,
            "fragments_found": rule_fragments
        }
    except Exception as e:
        print(f"An internal error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)