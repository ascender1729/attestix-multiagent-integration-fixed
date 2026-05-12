import os
from crewai import Agent, Task, Crew, Process

def run_audit_panel(discrepancy_report: str) -> str:
    """CrewAI Node: Cross-functional audit team debates the discrepancy report."""
    print("\n--- PHASE 2: CREWAI ESG AUDIT PANEL ---")
    print(" [CrewAI] Assembling the Audit Team...")
    
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

    labor_officer = Agent(
        role="Labor Rights Investigator",
        goal="Analyze the discrepancies regarding unpaid overtime, forced labor, and protests. Recommend immediate suspension of the supplier.",
        backstory="You are a strict human rights advocate. You do not tolerate any factory that abuses its workers.",
        verbose=True, allow_delegation=False
    )
    
    eco_officer = Agent(
        role="Environmental Compliance Officer",
        goal="Analyze the discrepancies regarding chemical spills and river pollution. Recommend massive fines or termination of the contract.",
        backstory="You are an environmental scientist. You believe corporate pollution is a crime and must be punished.",
        verbose=True, allow_delegation=False
    )
    
    supply_chain_manager = Agent(
        role="Corporate Supply Chain Manager",
        goal="Defend the supplier. Emphasize the $4.2M in cost savings. Argue that the news might be exaggerated and that finding a new factory will disrupt production.",
        backstory="You care about profit margins and logistics. You hate when ESG auditors slow down your supply chain.",
        verbose=True, allow_delegation=False
    )

    debate_task = Task(
        description=f"""
        Review the following Intelligence Discrepancy Report regarding one of our suppliers:
        
        {discrepancy_report}
        
        Debate the findings. The Labor and Eco Officers must argue for terminating the supplier due to severe ESG violations. The Supply Chain Manager must fight to keep the supplier to save $4.2M.
        Together, produce an 'Internal Audit Debate Report' outlining the risks, the financial impact, and the recommended actions.
        """,
        expected_output="A detailed report summarizing the arguments from the labor, environmental, and financial perspectives.",
        agent=labor_officer
    )

    crew = Crew(
        agents=[labor_officer, eco_officer, supply_chain_manager],
        tasks=[debate_task],
        process=Process.sequential,
        verbose=True
    )
    
    print(" [CrewAI] The ESG Audit debate has begun...")
    result = str(crew.kickoff())
    print(" [CrewAI] Internal Audit Debate Report generated.\n")
    return result
