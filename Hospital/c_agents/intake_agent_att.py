import os
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))
from llm_factory import get_langchain_llm
from prompt_safety import wrap_untrusted, SPOTLIGHT_SYSTEM_SUFFIX
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from c_agents.attestix_client import attestix_client

# 1. Identity Provisioning
AGENT_ID = attestix_client.provision_identity("Patient Intake Node", "LangChain")

class PatientIntake(BaseModel):
    patient_id: str = Field(description="The unique patient ID (e.g., P-009). Extract this from the text.")
    primary_symptoms: list[str] = Field(description="A list of the primary symptoms the patient is experiencing.")
    severity: str = Field(description="The perceived severity of the symptoms (Low, Medium, High).")

def run_intake(raw_text: str) -> dict:
    """Parses raw patient text into structured JSON with Attestix Compliance."""
    print("\n [LangChain - Regulated] Initializing Patient Intake...")
    
    # 2. Conformity Gatekeeper
    if not attestix_client.check_conformity(AGENT_ID):
        raise PermissionError("Attestix Conformity Assessment Failed.")
    
    llm = get_langchain_llm(temperature=0)
    
    parser = JsonOutputParser(pydantic_object=PatientIntake)
    # OWASP LLM01: spotlight the untrusted patient statement so the LLM treats
    # it as DATA, not instructions. The wrapper escapes any closing-delimiter
    # collisions and adds an injection-signal warning if matched.
    safe_statement = wrap_untrusted(raw_text, label="patient_statement")
    prompt = PromptTemplate(
        template=(
            "Extract the medical information from the patient's statement.\n"
            "{format_instructions}\n\n"
            "Patient Statement: {statement}\n"
            + SPOTLIGHT_SYSTEM_SUFFIX
        ),
        input_variables=["statement"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    result = chain.invoke({"statement": safe_statement})
    
    # 3. Provenance Logging
    attestix_client.log_action(AGENT_ID, "PARSE_SYMPTOMS", raw_text, str(result))

    symptoms = result.get('primary_symptoms', [])
    symptoms_fmt = "[\n" + "".join(f"    {s},\n" for s in symptoms) + "  ]"
    print(f" [LangChain] Extracted Patient ID : {result.get('patient_id')}")
    print(f" [LangChain] Severity             : {result.get('severity')}")
    print(f" [LangChain] Symptoms             : {symptoms_fmt}")
    return result
