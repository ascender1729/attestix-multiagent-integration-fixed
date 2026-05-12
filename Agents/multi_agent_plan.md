# 4-Agent Architecture Plan (Before Attestix)

## Use Case: AI Financial Investment Committee
We are building a 4-agent committee that processes a user's request (e.g., "Should I invest in Tesla right now?"), researches it, analyzes it, checks it for risk, and issues a final recommendation. 

This will serve as our "unregulated" base project. Later, we will inject Attestix to audit the agents, log their decisions to the blockchain, and prove EU AI Act compliance.

## The Agents (Powered by Groq)

| Agent Role | Groq Model | Purpose | Tool Access |
| :--- | :--- | :--- | :--- |
| **1. Market Researcher** | `llama3-8b-8192` | Extremely fast. Hits the web to gather the latest news on the target company. | `DuckDuckGo Search` (Free, no API key needed) |
| **2. Financial Analyst** | `mixtral-8x7b-32768` | Excellent at reasoning. Reads the news and extracts the bullish/bearish financial indicators. | None |
| **3. Risk Manager** | `gemma2-9b-it` | Specialized logic. Looks at the financial analysis and highlights critical market risks, regulatory risks, etc. | None |
| **4. Portfolio Manager** | `llama3-70b-8192` | Heavyweight reasoning. Takes the research, analysis, and risk factors, and writes the final cohesive investment report. | None |

## Architecture: LangGraph
We will use **LangGraph** to build this. LangGraph is perfect because it passes a shared "State" (like a shared document) from one agent to the next in a sequential pipeline.

### The Pipeline Flow:
`User Input` -> `Researcher` -> `Analyst` -> `Risk Manager` -> `Portfolio Manager` -> `Final Output`

## Next Steps
I will generate the `base_architecture.py` file in the `Agents` directory! 
To run it, we just need to install the required packages and set your `GROQ_API_KEY`. 

Are you ready to install the dependencies and test the base code before we add the Attestix compliance layers?
