import os
from crewai import Agent, Task, Crew, Process

def run_investment_committee(market_report: str, quant_strategy: str) -> str:
    """CrewAI Node: The Investment Committee debates the trade execution."""
    print("\n--- PHASE 3: CREWAI INVESTMENT COMMITTEE ---")
    print(" [CrewAI] Assembling the Trading Desk...")
    
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

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
    return result
