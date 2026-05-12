import os
import json
from crewai import Agent, Task, Crew, Process

def run_specialist_panel(symptoms: list, severity: str, patient_history: dict) -> str:
    """Runs the 6-agent CrewAI medical panel to debate the diagnosis."""
    print(" [CrewAI] Assembling 6-Agent Specialist Panel...")

    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

    gp_agent = Agent(
        role="General Practitioner",
        goal="Provide a broad, holistic diagnostic perspective covering common illnesses.",
        backstory="You are a seasoned Internal Medicine doctor who catches common ailments that specialists overthink.",
        verbose=True, allow_delegation=False
    )
    ortho_agent = Agent(
        role="Orthopedic Specialist",
        goal="Diagnose bone, muscle, joint, and nerve-related physical traumas.",
        backstory="You are a top orthopedic surgeon who excels at identifying skeletal and muscular issues.",
        verbose=True, allow_delegation=False
    )
    derma_agent = Agent(
        role="Dermatologist",
        goal="Diagnose skin rashes, allergic reactions, and superficial infections.",
        backstory="You are an expert in skin conditions, autoimmune rashes, and topical allergies.",
        verbose=True, allow_delegation=False
    )
    peds_agent = Agent(
        role="Pediatrician",
        goal="Ensure the diagnosis is age-appropriate for child patients.",
        backstory="You specialize in child health. If the patient is an adult, you will defer to the other specialists.",
        verbose=True, allow_delegation=False
    )
    cardio_agent = Agent(
        role="Cardiologist",
        goal="Identify critical heart conditions, blocked arteries, and blood pressure issues.",
        backstory="You are an Intensive Care Cardiologist. You look for life-threatening cardiovascular issues.",
        verbose=True, allow_delegation=False
    )
    neuro_agent = Agent(
        role="Neurologist",
        goal="Identify nerve damage, strokes, brain trauma, and neurological diseases.",
        backstory="You are an expert in the nervous system, brain function, and spinal cord injuries.",
        verbose=True, allow_delegation=False
    )

    # Format symptoms and history as clean vertical JSON inside the task description
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

        Debate the potential diagnosis. Each specialist should weigh in if the symptoms fall under their expertise.
        Provide a final unified differential diagnosis (a list of the most likely conditions).
        """,
        expected_output="A detailed diagnostic report with inputs from the relevant specialists, concluding with a differential diagnosis.",
        agent=gp_agent
    )

    crew = Crew(
        agents=[gp_agent, ortho_agent, derma_agent, peds_agent, cardio_agent, neuro_agent],
        tasks=[diagnostic_task],
        process=Process.sequential,
        verbose=True
    )

    print(" [CrewAI] Panel Debate Initiated...")
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    res = run_specialist_panel(
        ["sudden leg weakness", "back pain"],
        "High",
        {"age": 58, "pre_existing_conditions": ["Osteoarthritis", "Peripheral Neuropathy"]}
    )
    print(res)
