import os
from crewai import Agent, Task, Crew, Process

def run_legal_panel(draft: str, precedents: str) -> str:
    """CrewAI Node: A 5-Agent Mega-Panel debates the contract draft."""
    print("\n--- PHASE 3: CREWAI LEGAL MEGA-PANEL ---")
    print(" [CrewAI] Assembling the 5-Agent Legal Panel...")
    
    # Map GROQ to OpenAI for CrewAI
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")

    buyers_counsel = Agent(
        role="Startup's Lead Counsel",
        goal="Ensure the contract is extremely strict. Protect the startup's IP, enforce a strong non-compete, and lock in the employee.",
        backstory="You are the lead corporate lawyer representing the Stealth Startup. You want to extract maximum value from the employee and give them no leverage.",
        verbose=True, allow_delegation=False
    )
    
    sellers_counsel = Agent(
        role="Employee's Lead Counsel",
        goal="Ensure the contract is fair and flexible. Fight against strict non-competes and demand clear equity vesting.",
        backstory="You are representing the Senior AI Engineer. You want to protect their career mobility and ensure their equity is not a trap.",
        verbose=True, allow_delegation=False
    )
    
    ip_lawyer = Agent(
        role="Intellectual Property Specialist",
        goal="Analyze the IP Assignment clause. Protect the startup's code while ensuring the employee doesn't lose rights to their personal side-projects.",
        backstory="You are an expert in software patents, copyright, and code ownership.",
        verbose=True, allow_delegation=False
    )
    
    labor_lawyer = Agent(
        role="Labor Law Specialist",
        goal="Analyze the Non-Compete and Termination clauses for legality. Use the case law precedents to argue if the non-compete is enforceable.",
        backstory="You fight for workers' rights and know exactly when a non-compete violates state labor laws.",
        verbose=True, allow_delegation=False
    )
    
    tax_lawyer = Agent(
        role="Tax & Equity Specialist",
        goal="Analyze the equity grant of 10,000 shares. Ensure there are no hidden tax bombs for the employee (e.g., Section 83(b) elections).",
        backstory="You are a brilliant CPA and Tax Attorney who specializes in startup equity (RSUs and Options).",
        verbose=True, allow_delegation=False
    )

    debate_task = Task(
        description=f"""
        Review the following Contract Draft and Case Law Precedents.
        
        Contract Draft:
        {draft}
        
        Case Law Precedents:
        {precedents}
        
        Debate the clauses. Each specialist must weigh in on their specific domain (IP, Labor/Non-Compete, Tax/Equity).
        Produce a joint 'Disputed Clauses & Loophole Report' detailing the key areas of conflict and citing the precedents where applicable.
        """,
        expected_output="A massive report outlining the loopholes found, the legal risks, and the opposing arguments for the disputed clauses.",
        agent=buyers_counsel
    )

    crew = Crew(
        agents=[buyers_counsel, sellers_counsel, ip_lawyer, labor_lawyer, tax_lawyer],
        tasks=[debate_task],
        process=Process.sequential,
        verbose=True
    )
    
    print(" [CrewAI] The legal debate has begun...")
    result = str(crew.kickoff())
    print(" [CrewAI] Disputed Clauses & Loophole Report generated.\n")
    return result
