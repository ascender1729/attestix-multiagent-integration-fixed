import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Define the expected JSON structure
class PatientIntake(BaseModel):
    patient_id: str = Field(description="The unique patient ID (e.g., P-009). Extract this from the text.")
    primary_symptoms: list[str] = Field(description="A list of the primary symptoms the patient is experiencing.")
    severity: str = Field(description="The perceived severity of the symptoms (Low, Medium, High).")

def run_intake(raw_text: str) -> dict:
    """Parses raw patient text into structured JSON."""
    print(" [LangChain] Initializing Patient Intake...")
    
    # Initialize the Groq model
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    parser = JsonOutputParser(pydantic_object=PatientIntake)
    
    prompt = PromptTemplate(
        template="Extract the medical information from the patient's statement.\n{format_instructions}\n\nPatient Statement: {statement}\n",
        input_variables=["statement"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    result = chain.invoke({"statement": raw_text})
    symptoms = result.get('primary_symptoms', [])
    symptoms_fmt = "[\n" + "".join(f"    {s},\n" for s in symptoms) + "  ]"
    print(f" [LangChain] Extracted Patient ID : {result.get('patient_id')}")
    print(f" [LangChain] Severity             : {result.get('severity')}")
    print(f" [LangChain] Symptoms             : {symptoms_fmt}")
    return result

if __name__ == "__main__":
    # Test block
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    res = run_intake("Hi, I'm patient P-009, Thomas. My legs suddenly feel very weak and my back is killing me.")
    print(res)
