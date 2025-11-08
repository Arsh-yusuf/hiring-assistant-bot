import streamlit as st
import cohere
from config.settings import COHERE_API_KEY
from core import prompts
from core.utils import save_candidate

# =============================
# ✅ Initialize Cohere client
# =============================
co = cohere.Client(COHERE_API_KEY)

# ✅ Define primary + fallback model
PRIMARY_MODEL = "command-a-03-2025"      # Free-tier compatible model
FALLBACK_MODEL = "command-light"         # Lightweight backup

# =============================
# ✅ Map steps to prompts
# =============================
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

# =============================
# ✅ Session State Initialization
# =============================
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

# =============================
# ✅ App Configuration
# =============================
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
st.title("🤖 TalentScout Hiring Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =============================
# ✅ Greeting Message
# =============================
if st.session_state.step == 0 and not st.session_state.ended and len(st.session_state.messages) == 0:
    greeting = (
        "👋 Hello! I’m your **TalentScout Hiring Assistant**.\n\n"
        "I’ll ask you a few quick questions to understand your background "
        "and generate tailored technical interview questions.\n\n"
        "👉 You can type **exit** anytime to end the conversation.\n\n"
        "Let's begin with your full name."
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    with st.chat_message("assistant"):
        st.markdown(greeting)

# =============================
# ✅ Safe Chat Call Function
# =============================
def chat_with_model(prompt):
    """Safely call Cohere model with fallback."""
    try:
        response = co.chat(model=PRIMARY_MODEL, message=prompt)
        return response.text.strip()
    except Exception as e:
        st.warning(f"⚠️ Using fallback model due to: {e}")
        response = co.chat(model=FALLBACK_MODEL, message=prompt)
        return response.text.strip()

# =============================
# ✅ Fallback Response Generator
# =============================
def fallback_response(user_input):
    prompt = f"""
    The candidate replied: "{user_input}".
    Provide a polite, professional fallback response,
    asking them to clarify while keeping the flow of the interview.
    """
    return chat_with_model(prompt)

# =============================
# ✅ Chat Input
# =============================
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

        # Basic validation with fallback
        if current_step == "Email" and "@" not in user_input:
            bot_reply = fallback_response(user_input)
        elif current_step == "Phone Number" and (not user_input.isdigit() or len(user_input) != 10):
            bot_reply = fallback_response(user_input)
        else:
            # Save response
            st.session_state.candidate[current_step] = user_input
            st.session_state.step += 1

            # Generate technical questions when all steps done
            if st.session_state.step == len(steps):
                tech_stack = st.session_state.candidate["Tech Stack"]
                response = chat_with_model(prompts.TECH_QUESTION_PROMPT.format(tech_stack=tech_stack))
                st.session_state.questions = response
                save_candidate(st.session_state.candidate)

            # Ask next question or end
            if st.session_state.step < len(steps):
                ask_prompt = step_to_prompt[steps[st.session_state.step]]
                bot_reply = chat_with_model(ask_prompt)
            else:
                bot_reply = "✅ All details collected! Here’s a summary of your information and tailored interview questions."

    # =============================
    # ✅ Show Assistant Response
    # =============================
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
