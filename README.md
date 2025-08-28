# 🤖 TalentScout Hiring Assistant

An **AI-powered Hiring Assistant Chatbot** built with **Streamlit** and **Cohere**.  
This chatbot simulates the **initial candidate screening process** for a fictional recruitment agency **TalentScout**.  

It collects candidate details step by step, validates inputs, and generates **tailored technical interview questions** based on the declared tech stack. Candidate data is stored **securely in anonymized form** in `candidates.json`.

---

## ✨ Features

- **ChatGPT-like Interface** 🗨️  
  Candidates interact in a natural chat window using `st.chat_message` and `st.chat_input`.

- **Greeting & Exit Handling** 👋  
  Welcomes candidates and ends gracefully when they type `exit`, `quit`, or `bye`.

- **Information Gathering** 📝  
  Collects:  
  - Full Name  
  - Email Address  
  - Phone Number  
  - Years of Experience  
  - Desired Position  
  - Current Location  
  - Tech Stack  

- **Prompt-Driven Flow** 🎯  
  Uses carefully designed prompts to ask candidate questions in a professional tone.

- **Tech Stack Declaration & Technical Questions** 💻  
  Generates **3–5 interview questions** tailored to the candidate’s stack using Cohere’s LLM.  
  Example: `Python + Django` → Python/Django interview questions.

- **Context Handling & Fallback** 🔄  
  - If input is unclear (invalid email, phone < 10 digits, etc.), chatbot asks politely for clarification.  
  - Maintains flow and context across conversation.

- **Data Handling & Privacy** 🔐  
  - Candidate info is stored in `data/candidates.json`.  
  - Sensitive data (email, phone) is **masked** before saving.  
  - All stored data is **simulated/anonymized** → GDPR-friendly.

---

## 📂 Project Structure

  hiring-assistant-bot/
  │── app.py                # Main Streamlit app
  │── requirements.txt      # Dependencies
  │── README.md             # Documentation
  │
  ├── config/
  │   └── settings.py       # API key loading
  │
  ├── core/
  │   ├── prompts.py        # Prompt templates
  │   ├── utils.py          # Masking + data storage
  │   ├── chatbot.py        # Chatbot logic (calls Cohere, manages responses)
  │
  ├── data/
  │   └── candidates.json   # Simulated storage (anonymized)


---

## ⚙️ Installation & Setup

1. Clone Repo
```bash
git clone https://github.com/your-username/hiring-assistant-bot.git
cd hiring-assistant-bot


2. Install Dependencies

pip install -r requirements.txt


3. Set API Key
Create a .env file in root directory
COHERE_API_KEY=your_api_key_here

4. Run the App
streamlit run app.py



