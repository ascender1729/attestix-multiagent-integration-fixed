import os
from crewai import Agent, Task, Crew, Process

def run_counsel_debate(draft: str, requirements: str) -> str:
    """CrewAI Node: Buyer's vs Seller's counsel debates the contract draft."""
    print("\n--- PHASE 2: CREWAI OPPOSING COUNSEL ---")
    print(" [CrewAI] Assembling Plaintiff and Defense Lawyers...")
    
    # Map GROQ to OpenAI for CrewAI
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

    buyers_counsel = Agent(
        role="Buyer/Employer Legal Counsel",
        goal="Protect the interests of the party issuing the contract (the Buyer or Employer). Find loopholes that expose them to liability and suggest stricter clauses to protect them.",
        backstory="You are a cutthroat corporate lawyer who protects billion-dollar companies from liability. You want the contract to be as restrictive and favorable to your client as possible.",
        verbose=True, allow_delegation=False
    )
    
    sellers_counsel = Agent(
        role="Seller/Employee Legal Counsel",
        goal="Protect the interests of the party signing the contract (the Seller or Employee). Argue against unfair, overly restrictive, or ambiguous clauses that hurt your client.",
        backstory="You are a tenacious lawyer fighting for workers and startups. You despise overly broad non-competes, unlimited liability, and unfair arbitration clauses. You will fight to soften them.",
        verbose=True, allow_delegation=False
    )

    debate_task = Task(
        description=f"""
        Review the following Contract Draft which was generated based on these requirements: '{requirements}'.
        
        Contract Draft:
        {draft}
        
        Debate the clauses. The Buyer's Counsel must find ways to make it stricter, and the Seller's Counsel must argue against unfairness.
        Together, produce a joint 'Loopholes & Disputed Clauses Report' detailing the key areas of conflict.
        """,
        expected_output="A detailed report outlining the loopholes found and the opposing arguments for the disputed clauses.",
        agent=buyers_counsel
    )

    crew = Crew(
        agents=[buyers_counsel, sellers_counsel],
        tasks=[debate_task],
        process=Process.sequential,
        verbose=True
    )
    
    print(" [CrewAI] The legal debate has begun...")
    result = str(crew.kickoff())
    print(" [CrewAI] Loopholes & Disputed Clauses Report generated.\n")
    return result
