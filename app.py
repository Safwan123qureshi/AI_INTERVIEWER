import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# Page Settings
st.set_page_config(
    page_title="AI Interviewer",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 AI Interviewer")
st.subheader("Practice Interviews for University Students")

# Departments
role = st.selectbox(
    "Select Department",
    [
        "Computer Science",
        "Software Engineering",
        "Artificial Intelligence",
        "Data Science",
        "Cyber Security",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Telecommunication Engineering",
        "Computer Systems Engineering",
        "Industrial Engineering",
        "Mining Engineering",
        "Chemical Engineering",
        "Architecture",
        "Mathematics",
        "Physics"
    ]
)

# Session State
if "chat" not in st.session_state:
    st.session_state.chat = []

if "question_no" not in st.session_state:
    st.session_state.question_no = 0

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "finished" not in st.session_state:
    st.session_state.finished = False

# Sidebar
with st.sidebar:
    st.header("Interview Details")
    st.write("Department:", role)

# Start Interview
if st.button("🎤 Start Interview"):

    st.session_state.chat = []
    st.session_state.question_no = 1
    st.session_state.finished = False
    st.session_state.interview_started = True

    prompt = f"""
You are a friendly university interviewer.

The student belongs to:

{role}

Rules:
- Ask very simple questions.
- Keep questions short.
- Questions must be easy for students.
- Do not ask advanced industry questions.
- Do not ask long questions.
- Ask only ONE question.
- Do not give score.
- Do not give feedback.
- Ask questions only from {role}.

Start with the first question.
"""

    try:
        response = model.generate_content(prompt)

        st.session_state.chat.append(
            {"role": "AI", "text": response.text}
        )

    except Exception as e:
        st.error(f"Gemini API Error: {e}")

# Progress Bar
if st.session_state.interview_started:

    st.progress(
        min(st.session_state.question_no / 5, 1.0)
    )

    st.write(
        f"Question {min(st.session_state.question_no,5)} / 5"
    )

# Show Chat
for msg in st.session_state.chat:

    if msg["role"] == "AI":
        st.info(msg["text"])

    elif msg["role"] == "Candidate":
        st.success(msg["text"])

# Answer Section
if (
    st.session_state.interview_started
    and not st.session_state.finished
):

    answer = st.text_area(
        "Your Answer",
        key=f"answer_{st.session_state.question_no}"
    )

    if st.button("Submit Answer"):

        if answer.strip():

            st.session_state.chat.append(
                {
                    "role": "Candidate",
                    "text": answer
                }
            )

            # Final Evaluation
            if st.session_state.question_no >= 5:

                evaluation_prompt = f"""
Evaluate this interview:

{st.session_state.chat}

Give:

1. Overall Score out of 100
2. Strong Points
3. Weak Points
4. Final Feedback

Use simple language.
"""

                try:

                    response = model.generate_content(
                        evaluation_prompt
                    )

                    st.session_state.chat.append(
                        {
                            "role": "AI",
                            "text": response.text
                        }
                    )

                    st.session_state.finished = True

                except Exception as e:
                    st.error(f"Gemini API Error: {e}")

            else:

                next_prompt = f"""
You are a friendly university interviewer.

Student Department:

{role}

Previous Conversation:

{st.session_state.chat}

Rules:
- Ask only ONE new question.
- Keep question short.
- Keep question easy.
- Do not repeat previous questions.
- Do not give score.
- Do not give feedback.
- Ask only from {role}.

Ask the next question.
"""

                try:

                    response = model.generate_content(
                        next_prompt
                    )

                    st.session_state.chat.append(
                        {
                            "role": "AI",
                            "text": response.text
                        }
                    )

                    st.session_state.question_no += 1

                except Exception as e:
                    st.error(f"Gemini API Error: {e}")

            st.rerun()