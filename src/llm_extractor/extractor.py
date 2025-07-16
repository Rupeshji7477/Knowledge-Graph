# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser
# from pydantic import BaseModel, Field
# from langchain_google_genai import ChatGoogleGenerativeAI
# from typing import List
# from src.config import GOOGLE_API_KEY

# # Defines the desired JSON structure for the LLM output using Pydantic.
# class Conditions(BaseModel):
#     state: List[str] = Field(description="The state(s) the rule applies to. Use an empty list if not mentioned.")
#     property: List[str] = Field(description="The property type(s) the rule applies to. Use an empty list if not mentioned.")
#     form: List[str] = Field(description="The form ID(s) required by the rule. Use an empty list if not mentioned.")
#     programType: List[str] = Field(description="The program type(s) the rule applies to. Use an empty list if not mentioned.")
#     applicationType: List[str] = Field(description="The application type(s) the rule applies to. Use an empty list if not mentioned.")

# class ExtractedRule(BaseModel):
#     ruleName: str = Field(description="The official name of the business rule.")
#     conditions: Conditions = Field(description="The set of conditions that trigger the rule.")

# parser = PydanticOutputParser(pydantic_object=ExtractedRule)

# def get_extraction_chain():
#     """Builds and returns a LangChain chain for rule extraction."""
#     if not GOOGLE_API_KEY:
#         raise ValueError("Google API Key not found. Please set it in the .env file.")

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "You are an expert data extraction bot. Your goal is to extract rule information from text into a structured JSON format. You must follow the user's JSON schema precisely. If a value for a specific entity is not mentioned, use an empty list `[]`."),
#         ("human", "Please extract the rule information from the following text.\n{format_instructions}\n\nText:\n{rule_text}")
#     ]).partial(format_instructions=parser.get_format_instructions())

#     llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)
#     chain = prompt | llm | parser
#     return chain

# async def extract_information_from_text(rule_text: str):
#     """Invokes the LangChain extraction chain and returns the result as a dict."""
#     extraction_chain = get_extraction_chain()
#     print(f"--- Extracting from text using LangChain: {rule_text[:50]}...")
#     try:
#         result_pydantic = await extraction_chain.ainvoke({"rule_text": rule_text})
#         return result_pydantic.dict()
#     except Exception as e:
#         print(f"Error during LangChain extraction: {e}")
#         return None

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Literal
from src.config import GOOGLE_API_KEY

# NEW MODEL: Defines a single rule fragment
class RuleFragment(BaseModel):
    entityType: Literal["state", "property", "form", "account"] = Field(description="The type of the entity (e.g., 'state', 'form').")
    entityName: str = Field(description="The name of the entity (e.g., 'Florida', '03').")
    content: str = Field(description="Try to understand the relatioship of the entity with the rule. This is the rule content that applies to this entity.")

# NEW MODEL: The LLM will return a list of these fragments
class ExtractedData(BaseModel):
    fragments: List[RuleFragment] = Field(description="Try to extract all rule fragments from the text. Each fragment should be a specific rule tied to a single entity like a state, a form, or a property type. If no fragments are found, return an empty list.")

# Update the parser to use the new top-level model
parser = PydanticOutputParser(pydantic_object=ExtractedData)

def get_extraction_chain():
    """Builds the updated LangChain chain for fragment extraction."""
    if not GOOGLE_API_KEY:
        raise ValueError("Google API Key not found. Please set it in the .env file.")

    # NEW PROMPT: Instructs the LLM to find and separate individual rule fragments.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert data extraction bot. Your task is to read a text and identify all individual rule fragments. A fragment is a specific rule tied to a single entity like a state, a form, or a property type. Deconstruct the text into a list of these fragments according to the JSON schema."),
        ("human", "Please extract all rule fragments from the following text.\n{format_instructions}\n\nText:\n{rule_text}")
    ]).partial(format_instructions=parser.get_format_instructions())

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)
    chain = prompt | llm | parser
    return chain

async def extract_fragments_from_text(rule_text: str):
    """Invokes the LangChain chain for fragment extraction."""
    extraction_chain = get_extraction_chain()
    print(f"--- Extracting fragments from text: {rule_text[:50]}...")
    try:
        result_pydantic = await extraction_chain.ainvoke({"rule_text": rule_text})
        return result_pydantic.dict()
    except Exception as e:
        print(f"Error during LangChain fragment extraction: {e}")
        return None   
    