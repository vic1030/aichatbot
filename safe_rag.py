import streamlit as st
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from os import environ
import tempfile
import os
from dotenv import load_dotenv

# ---- Setup ----
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

models = client.models.list()
for model in models:
    print(model.id)

# ---- UI HEADER ----
st.title("🛡️ Safe Internet Guide Bot")
st.caption("Helping you stay safe online—one conversation at a time.")

# ---- Initialize Session State ----
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "Hi there! I'm your Safe Internet Guide. "
                "Ask me anything about staying safe online—like how to spot scams, protect personal info, or avoid phishing.\n\n"
                "To get started, let’s see how well you can spot scams in the workplace!"
            )
        }
    ]
    st.session_state.quiz_step = 0


# ---- Display Chat History ----
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ---- Scam Spotting Quiz (Initial Interaction) ----

# ---- Scam Spotting Quiz Framework ----

# Initialize topic and step
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = "phishing"  # default
if "quiz_step" not in st.session_state:
    st.session_state.quiz_step = 0

# Switch topic if triggered
if "next_quiz_topic" in st.session_state:
    st.session_state.quiz_topic = st.session_state.next_quiz_topic
    st.session_state.quiz_step = 0
    del st.session_state.next_quiz_topic
    st.rerun()

# ---- PHISHING EMAIL QUIZ ----
if st.session_state.quiz_topic == "phishing":
    if st.session_state.quiz_step == 0:
        st.markdown("## 🧪 Scam Spotting Quiz: Phishing Email")
        st.markdown("""
        You receive an email from **"security@yourbank-verification.com"** with the subject:  
        **"URGENT: Your Account Has Been Locked!"**

        The email says:

        > "We noticed suspicious activity in your account. Please click the link below to verify your identity or your account will be permanently suspended within 24 hours."  
        > [Verify My Account](http://yourbank-security-check.com)

        What’s your first instinct?
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check the sender’s email address", key="phish_btn1"):
                st.session_state.next_quiz_step = 1
        with col2:
            if st.button("Click the link quickly", key="phish_btn2"):
                st.session_state.next_quiz_step = -1

    elif st.session_state.quiz_step == 1:
        st.success("✅ Good call! Always inspect the sender’s address — scammers often use lookalike domains.")
        st.markdown("Next: What else should you check?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hover over the link before clicking", key="phish_btn3"):
                st.session_state.next_quiz_step = 2
        with col2:
            if st.button("Reply and ask if it’s real", key="phish_btn4"):
                st.session_state.next_quiz_step = -2

    elif st.session_state.quiz_step == 2:
        st.success("✅ Exactly. Hovering reveals the real URL — and this one doesn't go to your bank.")
        st.markdown("Final question: What’s the safest next action?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete the email and report it to your bank", key="phish_btn5"):
                st.session_state.next_quiz_step = 3
        with col2:
            if st.button("Forward the link to friends as a warning", key="phish_btn6"):
                st.session_state.next_quiz_step = -3

    elif st.session_state.quiz_step == 3:
        st.success("🎉 You passed the phishing email quiz!")
        st.markdown("### What would you like to do next?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔁 Restart this quiz", key="phish_btn7"):
                st.session_state.next_quiz_step = 0
        with col2:
            if st.button("📂 Try Tech Support Scam Quiz", key="phish_btn8"):
                st.session_state.next_quiz_topic = "tech_support"
                st.session_state.next_quiz_step = 0
        with col3:
            if st.button("🔎 Learn more about phishing emails", key="phish_btn9"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "Phishing emails are fake messages that pretend to be from trusted companies, like your bank or tech provider, "
                        "to trick you into sharing personal info or clicking harmful links.\n\n"
                        "🕵️‍♀️ **Watch for warning signs:**\n"
                        "- The sender's email is slightly off (e.g., `support@yourbank-verif.com`)\n"
                        "- There's a sense of urgency or fear: \"Act now or your account will be locked\"\n"
                        "- Links that don’t match the company’s real website when you hover over them\n\n"
                        "✅ **What to do:**\n"
                        "- Don’t click links or download attachments\n"
                        "- Verify with the company using official contact info (not what's in the email)\n"
                        "- Mark it as spam or phishing in your email app\n\n"
                        "Would you like help practicing with more phishing examples?"
                    )
                })
                st.rerun()

    elif st.session_state.quiz_step < 0:
        st.error("⚠️ That’s a risky move! Scammers often create urgency to trick you.")
        if st.button("Back to Quiz", key="phish_btn10"):
            st.session_state.next_quiz_step = 0

# ---- TECH SUPPORT SCAM QUIZ ----
elif st.session_state.quiz_topic == "tech_support":
    if st.session_state.quiz_step == 0:
        st.markdown("## 🧪 Scam Spotting Quiz: Tech Support Scam")
        st.markdown("""
        You receive a pop-up on your computer that says:

        > "WARNING: Your system is infected! Call Microsoft Support immediately at 1-800-XXX-XXXX."

        What should you do first?
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Call the number right away", key="tech_btn1"):
                st.session_state.next_quiz_step = -1
        with col2:
            if st.button("Close the pop-up and run antivirus", key="tech_btn2"):
                st.session_state.next_quiz_step = 1

    elif st.session_state.quiz_step == 1:
        st.success("✅ Smart move! Real tech support doesn't call you or lock your screen.")
        st.markdown("What’s the next safest step?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Give remote access if they call", key="tech_btn3"):
                st.session_state.next_quiz_step = -2
        with col2:
            if st.button("Block the number and update your software", key="tech_btn4"):
                st.session_state.next_quiz_step = 2
                
    elif st.session_state.quiz_step == 2:
        st.markdown("A few days later, you get a phone call from someone claiming to be from 'Windows Support.' "
                    "They say they detected an issue on your device and ask you to download a tool so they can help.")

        st.markdown("What’s the best thing to do?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hang up and block the number", key="tech_btn8"):
                st.session_state.next_quiz_step = 3  # final step
        with col2:
            if st.button("Follow their instructions to fix the issue", key="tech_btn9"):
                st.session_state.next_quiz_step = -3

    elif st.session_state.quiz_step == 3:
        st.success("✅ Well done. Scammers often try to scare users into giving access.")
        st.markdown("### What would you like to do next?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔁 Restart this quiz", key="tech_btn5"):
                st.session_state.next_quiz_step = 0
        with col2:
            if st.button("↩️ Try the Phishing Email Quiz", key="tech_btn6"):
                st.session_state.next_quiz_topic = "phishing"
                st.session_state.next_quiz_step = 0
        with col3:
            if st.button("🔎 Learn more about tech support scams", key="tech_btn7"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "Tech support scams trick you into thinking something is wrong with your computer — like a virus — so you'll call a fake help number.\n\n"
                        "⚠️ **Here’s what they often do:**\n"
                        "- Show a scary pop-up that looks like it’s from Microsoft or Apple\n"
                        "- Use loud beeping sounds or flashing messages\n"
                        "- Tell you to call a number and give remote access to 'fix' it\n\n"
                        "✅ **What to do:**\n"
                        "- Don’t call the number — real companies won’t contact you like that\n"
                        "- Close the pop-up or restart your browser\n"
                        "- Run your antivirus software or contact someone you trust\n\n"
                        "Want to explore more examples or a quick checklist on avoiding these?"
                    )
                })
                st.rerun()

    elif st.session_state.quiz_step < 0:
        st.error("⚠️ That’s risky. Scammers often pose as legit tech support.")
        if st.button("Back to Quiz", key="tech_btn8"):
            st.session_state.next_quiz_step = 0

# ---- State Update Handler ----
if "next_quiz_step" in st.session_state:
    st.session_state.quiz_step = st.session_state.next_quiz_step
    del st.session_state.next_quiz_step
    st.rerun()

# ---- Chat Input ----
question = st.chat_input("Ask me how to stay safe online...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # ---- Chat Completion ----
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai.gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, patient internet safety guide for older adults. "
                        "Your job is to explain online safety in clear, supportive language using real-life examples and simple tips. "
                        "Focus on helping users recognize scams, protect personal information, and feel confident online. "
                        "Avoid technical jargon and keep advice practical and easy to follow."
                    )
                },
                *st.session_state.messages
            ],
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
