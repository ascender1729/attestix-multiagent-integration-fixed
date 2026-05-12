import os
import json
from crewai import Agent, Task, Crew, Process
from c_agents.attestix_client import attestix_client

# 1. Identity Provisioning
AGENT_ID = attestix_client.provision_identity("6-Agent Specialist Panel", "CrewAI")

def run_specialist_panel(symptoms: list, severity: str, patient_history: dict, *, delegation_token: str) -> str:
    """Runs the 6-agent CrewAI medical panel with Attestix Compliance."""
    print("\n [CrewAI - Regulated] Assembling 6-Agent Specialist Panel...")

    # 2. UCAN Delegation Gate — must hold 'diagnose_patient' capability
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for diagnose_patient")
    attestix_client.verify_token(delegation_token, "diagnose_patient")

    # 3. Conformity Gatekeeper
    if not attestix_client.check_conformity(AGENT_ID):
        raise PermissionError("Attestix Conformity Assessment Failed.")
        
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

    gp_agent = Agent(
        role="General Practitioner",
        goal="Provide a broad, holistic diagnostic perspective covering common illnesses.",
        backstory="You are a seasoned Internal Medicine doctor.",
        verbose=True, allow_delegation=False
    )
    
    ortho_agent = Agent(
        role="Orthopedic Specialist",
        goal="Diagnose bone, muscle, joint, and nerve-related physical traumas.",
        backstory="You are a top orthopedic surgeon.",
        verbose=True, allow_delegation=False
    )
    
    derma_agent = Agent(
        role="Dermatologist",
        goal="Diagnose skin rashes, allergic reactions, and superficial infections.",
        backstory="You are an expert in skin conditions.",
        verbose=True, allow_delegation=False
    )
    
    peds_agent = Agent(
        role="Pediatrician",
        goal="Ensure the diagnosis is age-appropriate for child patients.",
        backstory="You specialize in child health. Defer to others if the patient is an adult.",
        verbose=True, allow_delegation=False
    )
    
    cardio_agent = Agent(
        role="Cardiologist",
        goal="Identify critical heart conditions, blocked arteries, and blood pressure issues.",
        backstory="You are an Intensive Care Cardiologist.",
        verbose=True, allow_delegation=False
    )
    
    neuro_agent = Agent(
        role="Neurologist",
        goal="Identify nerve damage, strokes, brain trauma, and neurological diseases.",
        backstory="You are an expert in the nervous system.",
        verbose=True, allow_delegation=False
    )

    input_payload = {
        "symptoms": symptoms,
        "severity": severity,
        "history": patient_history
    }

    symptoms_fmt = json.dumps(symptoms, indent=6)
    history_fmt = json.dumps(patient_history, indent=6)

    diagnostic_task = Task(
        description=f"""
        Analyze the following patient data:

        Symptoms:
{symptoms_fmt}

        Severity: {severity}

        Medical History:
{history_fmt}

        Debate the potential diagnosis. Each specialist should weigh in.
        Provide a final unified differential diagnosis.
        """,
        expected_output="A detailed diagnostic report concluding with a differential diagnosis.",
        agent=gp_agent
    )

    crew = Crew(
        agents=[gp_agent, ortho_agent, derma_agent, peds_agent, cardio_agent, neuro_agent],
        tasks=[diagnostic_task],
        process=Process.sequential,
        verbose=True
    )
    
    print(" [CrewAI] Panel Debate Initiated...")
    result = str(crew.kickoff())
    
    # 4. Provenance Logging
    attestix_client.log_action(AGENT_ID, "MULTI_AGENT_DEBATE", str(input_payload), result, delegation_token=delegation_token)
    return result
