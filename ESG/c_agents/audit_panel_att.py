import os
from crewai import Agent, Task, Crew, Process
from c_agents.attestix_client import attestix_client

def run_audit_panel(discrepancy_report: str, agent_id: str, *, delegation_token: str) -> str:
    """CrewAI Node: Cross-functional audit team debates the discrepancy report (Regulated)."""
    print("\n--- PHASE 2: CREWAI ESG AUDIT PANEL ---")
    print(" [CrewAI - Regulated] Assembling the Audit Team...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for review_discrepancies")
    attestix_client.verify_token(delegation_token, "review_discrepancies")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")

    import sys as _sys


    from pathlib import Path as _Path


    _sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))


    from llm_factory import configure_crewai_env


    configure_crewai_env()

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
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="MULTI_AGENT_DEBATE",
        input_data=discrepancy_report,
        output_data=result,
        delegation_token=delegation_token
    )
    
    return result
