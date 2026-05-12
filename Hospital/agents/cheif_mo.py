import os
from openai import OpenAI

def run_cmo_ruling(crew_debate_output: str, patient_history: dict) -> str:
    """The Chief Medical Officer reviews the CrewAI debate and makes a final ruling."""
    print(" [OpenAI] Chief Medical Officer reviewing the case...")
    
    # We use the official OpenAI framework, but route the traffic to Groq for free
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    system_prompt = """
    You are the Chief Medical Officer of a highly regulated hospital.
    You will be provided with:
    1. A debate from your specialist panel (CrewAI output).
    2. The patient's secure medical history (Semantic Kernel output).
    
    Your job is to:
    1. Review the panel's differential diagnosis.
    2. Cross-reference it with the patient's known allergies and medications to ensure no fatal drug interactions.
    3. Issue a FINAL, authoritative diagnosis and a recommended treatment plan.
    Keep the final report professional, concise, and structured.
    Do NOT include a signature line or placeholder like [Your Name]. End the report after the recommendations.
    """
    
    user_prompt = f"""
    --- PATIENT HISTORY ---
    {patient_history}
    
    --- SPECIALIST PANEL DEBATE ---
    {crew_debate_output}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    
    final_ruling = response.choices[0].message.content
    print(" [OpenAI] Final Medical Ruling Issued.")
    return final_ruling

if __name__ == "__main__":
    pass
