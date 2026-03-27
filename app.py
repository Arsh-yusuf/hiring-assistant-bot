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
if "submitted" not in st.session_state:
    st.session_state.submitted = False

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
    """Safely call Cohere model with system preamble."""
    try:
        response = co.chat(
            model=PRIMARY_MODEL,
            message=prompt,
            preamble=prompts.SYSTEM_PROMPT
        )
        return response.text.strip()
    except Exception as e:
        st.warning(f"⚠️ Using fallback model due to: {e}")
        response = co.chat(
            model=FALLBACK_MODEL,
            message=prompt,
            preamble=prompts.SYSTEM_PROMPT
        )
        return response.text.strip()

# =============================
# ✅ Validation Logic
# =============================
def validate_with_llm(field, user_input):
    """Use LLM to check if the input is plausible for the given field."""
    prompt = f"The user provided '{user_input}' as their {field}. Is this a plausible and reasonable {field}? Answer only YES or NO."
    try:
        # Use a minimal call without the full system prompt for speed and accuracy
        response = co.chat(model=PRIMARY_MODEL, message=prompt).text.strip().upper()
        return "YES" in response
    except:
        return True # Fallback to True if LLM fails

def validate_input(step_name, user_input):
    """Perform basic client-side validation + LLM check for names."""
    if not user_input or len(user_input.strip()) < 2:
        return False
    
    clean_input = user_input.strip().lower()
    blacklist = ["nothing", "none", "n/a", "asdf", "test", "bullshit", "abc", "xyz", "no", "yes"]
    if clean_input in blacklist:
        return False

    if step_name == "Full Name":
        # First check heuristics
        has_letters = any(c.isalpha() for c in user_input)
        no_numbers = not any(c.isdigit() for c in user_input)
        if not (has_letters and no_numbers):
            return False
        # Then check plausibility with LLM
        return validate_with_llm("Full Name", user_input)
    
    if step_name == "Email":
        return "@" in user_input and "." in user_input
    if step_name == "Phone Number":
        # Strip common formatting characters
        clean_phone = user_input.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15
    if step_name == "Years of Experience":
        return any(char.isdigit() for char in user_input)
    return True

# =============================
# ✅ End of Interview UI
# =============================
if st.session_state.step == len(steps):
    st.subheader("📌 Candidate Summary")
    st.json(st.session_state.candidate)

    st.subheader("📝 Technical Interview Questions")
    if st.session_state.questions:
        st.markdown(st.session_state.questions)
    else:
        with st.spinner("Generating tailored questions..."):
            tech_stack = st.session_state.candidate.get("Tech Stack", "")
            st.session_state.questions = chat_with_model(prompts.TECH_QUESTION_PROMPT.format(tech_stack=tech_stack))
            st.rerun()
    
    st.divider()
    if not st.session_state.submitted:
        st.subheader("📤 Submit Your Solutions")
        st.info("Please upload your technical solutions (PDF or DOCX) to the questions above.")
        uploaded_file = st.file_uploader("Upload your solutions", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            # In a real app, you'd save the file here
            st.session_state.submitted = True
            st.success("File uploaded successfully!")
            st.rerun()
    else:
        st.success("🎉 Thank you! We have received your solutions and will get back to you shortly.")

# =============================
# ✅ Chat Input
# =============================
# Disable input if the interview is done or solution is submitted
input_disabled = st.session_state.step >= len(steps) or st.session_state.ended or st.session_state.submitted
user_input = st.chat_input("Your answer:", disabled=input_disabled)

if user_input and not st.session_state.ended:
    # Show user bubble
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Exit handling
    if user_input.lower() in ["exit", "quit", "bye"]:
        bot_reply = "🙏 Thank you for your time! TalentScout will review your details and get back to you soon. Have a great day!"
        st.session_state.ended = True

    else:
        current_step = steps[st.session_state.step]

        # Validation
        if not validate_input(current_step, user_input):
            # Generate a polite rejection/retry message using LLM
            validation_msg = prompts.VALIDATION_PROMPT.format(field=current_step, user_input=user_input)
            bot_reply = chat_with_model(validation_msg)
        else:
            # Save valid response
            st.session_state.candidate[current_step] = user_input
            st.session_state.step += 1

            # Check if we just finished the last step
            if st.session_state.step == len(steps):
                save_candidate(st.session_state.candidate)
                bot_reply = "✅ All details collected! Here’s a summary of your information and tailored interview questions."
            else:
                # Ask next question
                next_step = steps[st.session_state.step]
                ask_prompt = step_to_prompt[next_step]
                bot_reply = chat_with_model(ask_prompt)

    # Add bot reply to history and rerun
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()
