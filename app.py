import streamlit as st
import cohere
from config.settings import COHERE_API_KEY
from core import prompts
from core.utils import save_candidate

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Map steps to prompts
step_to_prompt = {
    "Full Name": prompts.ASK_NAME_PROMPT,
    "Email": prompts.ASK_EMAIL_PROMPT,
    "Phone Number": prompts.ASK_PHONE_PROMPT,
    "Years of Experience": prompts.ASK_EXPERIENCE_PROMPT,
    "Desired Position": prompts.ASK_POSITION_PROMPT,
    "Current Location": prompts.ASK_LOCATION_PROMPT,
    "Tech Stack": prompts.ASK_TECHSTACK_PROMPT,
}

steps = list(step_to_prompt.keys())

# Session state
if "step" not in st.session_state:
    st.session_state.step = 0
if "candidate" not in st.session_state:
    st.session_state.candidate = {}
if "questions" not in st.session_state:
    st.session_state.questions = None
if "ended" not in st.session_state:
    st.session_state.ended = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# App config
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
st.title("🤖 TalentScout Hiring Assistant")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Greeting
if st.session_state.step == 0 and not st.session_state.ended and len(st.session_state.messages) == 0:
    greeting = (
        "👋 Hello! I’m your **TalentScout Hiring Assistant**.\n\n"
        "I’ll ask you a few quick questions to understand your background "
        "and generate tailored technical interview questions.\n\n"
        "👉 You can type **exit** anytime to end the conversation.\n\n"
        "Let's begin with your full name"
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    with st.chat_message("assistant"):
        st.markdown(greeting)

# Fallback mechanism
def fallback_response(user_input):
    prompt = f"""
    The candidate replied: "{user_input}".
    Provide a polite, professional fallback response,
    asking them to clarify while keeping the flow of the interview.
    """
    response = co.chat(model="command-a-03-2025", message=prompt)
    return response.text.strip()

# Chat input
user_input = st.chat_input("Your answer:")

if user_input and not st.session_state.ended:
    # Show user bubble
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Exit handling
    if user_input.lower() in ["exit", "quit", "bye"]:
        bot_reply = "🙏 Thank you for your time! TalentScout will review your details and get back to you soon."
        st.session_state.ended = True

    else:
        current_step = steps[st.session_state.step]

        # Basic validation
        if current_step == "Email" and "@" not in user_input:
            bot_reply = fallback_response(user_input)
        elif current_step == "Phone Number" and (not user_input.isdigit() or len(user_input) != 10):
            bot_reply = fallback_response(user_input)
        else:
            # Save response
            st.session_state.candidate[current_step] = user_input
            st.session_state.step += 1

            # Generate questions if finished
            if st.session_state.step == len(steps):
                tech_stack = st.session_state.candidate["Tech Stack"]
                response = co.chat(model="command-r", message=prompts.TECH_QUESTION_PROMPT.format(tech_stack=tech_stack))
                st.session_state.questions = response.text.strip()
                save_candidate(st.session_state.candidate)  # save securely

            # Ask next question using Cohere prompt
            if st.session_state.step < len(steps):
                ask_prompt = step_to_prompt[steps[st.session_state.step]]
                ask_response = co.chat(model="command-r", message=ask_prompt)
                bot_reply = ask_response.text.strip()
            else:
                bot_reply = "✅ All details collected! Here’s a summary of your information and tailored interview questions."

    # Show assistant bubble
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

        if st.session_state.step == len(steps):
            st.subheader("📌 Candidate Summary")
            st.json(st.session_state.candidate)

            st.subheader("📝 Technical Interview Questions")
            if st.session_state.questions:
                st.markdown(st.session_state.questions)
            else:
                st.write("Generating questions...")



