from langchain_neo4j import GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_API_KEY
from langchain_community.graphs import Neo4jGraph

def ask_question(query, chain):
    """Helper function to run the QA chain and print results."""
    print("-" * 30)
    print(f"Human Question: {query}")
    try:
        result = chain.invoke({"query": query})
        print("\nLLM-Generated Answer:")
        print(result['result'])
    except Exception as e:
        print(f"An error occurred: {e}")
    print("-" * 30)


def main():
    """Sets up the natural language querying tool and asks questions."""
    if not GOOGLE_API_KEY:
        raise ValueError("Google API Key not found. Please set it in the .env file.")

    # Connect to the Neo4j database
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
    graph.refresh_schema()

    # Create the QA Chain
    chain = GraphCypherQAChain.from_llm(
        llm=ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, google_api_key=GOOGLE_API_KEY),
        graph=graph,
        verbose=True, # Shows the generated Cypher query
    )

    # --- Ask Questions ---
    ask_question("Which rule applies to residential properties in Texas?", chain)
    ask_question("How many forms are associated with the 'Lone Star Multi-Form Residential Rule'?", chain)
    ask_question("List all rules that apply to the 'Renewal' program type.", chain)

if __name__ == "__main__":
    main()