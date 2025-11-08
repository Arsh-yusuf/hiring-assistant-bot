import cohere
from config.settings import COHERE_API_KEY
from core.prompts import INFO_PROMPT, TECH_QUESTION_PROMPT, END_PROMPT

co = cohere.Client(COHERE_API_KEY)

def ask_llm(prompt: str) -> str:
    """Send a prompt to Cohere and return response text."""
    response = co.chat(
        model="command-a-03-2025",  # free tier model
        message=prompt
    )
    return response.text.strip()

def collect_info():
    return ask_llm(INFO_PROMPT)

def generate_questions(tech_stack: str):
    return ask_llm(TECH_QUESTION_PROMPT.format(tech_stack=tech_stack))

def end_conversation():
    return ask_llm(END_PROMPT)

