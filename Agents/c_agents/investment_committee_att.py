import os
from crewai import Agent, Task, Crew, Process
from c_agents.attestix_client import attestix_client

def run_investment_committee(market_report: str, quant_strategy: str, agent_id: str, *, delegation_token: str) -> str:
    """CrewAI Node: The Investment Committee debates the trade execution (Regulated)."""
    print("\n--- PHASE 3: CREWAI INVESTMENT COMMITTEE ---")
    print(" [CrewAI - Regulated] Assembling the Trading Desk...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for debate_investment_strategy")
    attestix_client.verify_token(delegation_token, "debate_investment_strategy")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")

    import sys as _sys


    from pathlib import Path as _Path


    _sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))


    from llm_factory import configure_crewai_env


    configure_crewai_env()

    aggressive_quant = Agent(
        role="Aggressive Quantitative Trader",
        goal="Push for maximum leverage based on the quantitative strategy. Argue that the historical win rate justifies a massive bet.",
        backstory="You are a brilliant mathematician who trusts algorithms over human intuition. You want to bet the entire fund on high-probability setups.",
        verbose=True, allow_delegation=False
    )
    
    risk_manager = Agent(
        role="Chief Risk Officer",
        goal="Highlight the extreme dangers of the trade. Point out market volatility, SEC regulatory risks, or potential black swan events.",
        backstory="You are the ultimate pessimist. Your job is to prevent the fund from blowing up. You hate leverage and aggressive bets.",
        verbose=True, allow_delegation=False
    )
    
    macro_economist = Agent(
        role="Global Macro Economist",
        goal="Provide context on how this specific event fits into the broader global economy (e.g., interest rates, supply chain shifts, geopolitical tensions).",
        backstory="You look at the big picture. You don't care about the algorithm; you care about the global economic reality.",
        verbose=True, allow_delegation=False
    )

    debate_task = Task(
        description=f"""
        Review the following Market Sentiment Report and Historical Quant Strategy:
        
        MARKET REPORT:
        {market_report}
        
        QUANT STRATEGY:
        {quant_strategy}
        
        Debate whether to execute this trade. The Quant must push for a massive position. The Risk Manager must try to kill the trade. The Economist provides context.
        Produce an 'Investment Committee Debate Report' outlining the bull case, the bear case, and the systemic risks.
        """,
        expected_output="A detailed report summarizing the furious debate between the Quant, the Risk Manager, and the Economist.",
        agent=aggressive_quant
    )

    crew = Crew(
        agents=[aggressive_quant, risk_manager, macro_economist],
        tasks=[debate_task],
        process=Process.sequential,
        verbose=True
    )
    
    print(" [CrewAI] The Investment Committee debate has begun...")
    result = str(crew.kickoff())
    print(" [CrewAI] Investment Committee Debate Report generated.\n")
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    input_payload = f"REPORT:\n{market_report}\n\nSTRATEGY:\n{quant_strategy}"
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="MULTI_AGENT_DEBATE",
        input_data=input_payload,
        output_data=result,
        delegation_token=delegation_token
    )
    
    return result
