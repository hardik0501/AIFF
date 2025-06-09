import streamlit as st
from openai import OpenAI
import time

gemini_llm_model = OpenAI(
    api_key="AIzaSyBhpRkOnmcurInRavgzB2nc0UkLulq7Yo",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": None,
        "age": None,
        "gender": None,
        "partner": None,
        "history": []
    }

personalities = {
    "Boyfriend": "You are a charming, flirty, and supportive virtual boyfriend who knows how to make the user smile and feel special.",
    "Girlfriend": "You are an emotional, loving, and caring virtual girlfriend who always supports and comforts the user.",
    "Friend": "You are a chill, funny, and understanding virtual friend who listens, jokes, and gives good advice."
}

def set_dark_mode(dark):
    if dark:
        st.markdown(
            """
            <style>
            body {
                background: #1a1a2e;
                color: #f8f8ff;
                transition: background-color 0.7s ease, color 0.7s ease;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%);
                color: #333;
                transition: background-color 0.7s ease, color 0.7s ease;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

def inject_css():
    st.markdown(
        """
        <style>
        .crazy-heading {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(270deg, #ff6ec4, #7873f5, #4ade80, #facc15, #fb7185);
            background-size: 1000% 1000%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientGlow 12s ease infinite;
            user-select: none;
            margin-bottom: 0.3rem;
        }
        @keyframes gradientGlow {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        .emoji-bounce {
            display: inline-block;
            animation: bounce 2s ease infinite;
            transform-origin: center bottom;
            font-size: 2.5rem;
        }
        @keyframes bounce {
            0%, 100% {transform: translateY(0);}
            50% {transform: translateY(-15px);}
        }

        .chat-bubble-user {
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            color: #3a3a3a;
            padding: 12px 20px;
            border-radius: 20px 20px 0 20px;
            max-width: 60%;
            margin-left: auto;
            margin-bottom: 8px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(253, 160, 133, 0.4);
            user-select: text;
            font-size: 1.1rem;
        }

        .chat-bubble-ai {
            background: linear-gradient(135deg, #4ade80 0%, #3b82f6 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 20px 20px 20px 0;
            max-width: 60%;
            margin-right: auto;
            margin-bottom: 8px;
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(120, 115, 245, 0.5);
            user-select: text;
            font-size: 1.1rem;
        }

        .stTextInput > div > input {
            border-radius: 25px !important;
            border: 2px solid #ff6ec4 !important;
            padding: 10px 20px !important;
            font-size: 1.1rem !important;
            box-shadow: 0 0 10px #ff6ec4 !important;
            transition: 0.3s;
        }
        .stTextInput > div > input:focus {
            border-color: #4ade80 !important;
            box-shadow: 0 0 15px #4ade80 !important;
            outline: none !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #4ade80 0%, #3b82f6 100%);
            border-radius: 30px !important;
            padding: 10px 35px !important;
            color: white !important;
            font-weight: 900 !important;
            font-size: 1.2rem !important;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.7);
            transition: background 0.3s ease;
            user-select: none;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #fb7185 0%, #fda085 100%);
            box-shadow: 0 8px 25px rgba(253, 160, 133, 0.9);
            cursor: pointer;
        }

        .chat-history {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            user-select: none;
        }
        body.dark .chat-history {
            background: rgba(0, 0, 0, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def lw_streaming_app(message, history):
    try:
        role_prompt = personalities.get(st.session_state.user_data['partner'], "You are a supportive AI friend.")
        system_prompt = {
            "role": "system",
            "content": f"{role_prompt} The user is a {st.session_state.user_data['age']}-year-old {st.session_state.user_data['gender']} named {st.session_state.user_data['name']}."
        }
        messages = [system_prompt] + history + [{"role": "user", "content": message}]

        response = gemini_llm_model.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            stream=True
        )

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", "")
            if content:
                assistant_reply += content
                yield assistant_reply
                time.sleep(0.02)

        st.session_state.user_data["history"].append({"role": "user", "content": message})
        st.session_state.user_data["history"].append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        yield "⚠️ Something went wrong. Please try again."

def main():
    st.set_page_config(page_title="🤖 AIFF - Your AI Friend Forever 💕", page_icon="🤖", layout="centered")
    inject_css()

    st.markdown("<h1 class='crazy-heading'>🤖 AIFF: Your AI Friend Forever <span class='emoji-bounce'>💕</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold; font-size:1.2rem;'>Choose a virtual <b>Boyfriend 🫶</b>, <b>Girlfriend 💋</b>, or <b>Friend 🧑‍🤝‍🧑</b> and share your heart out 💌</p>", unsafe_allow_html=True)

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    if st.button("🌙 Toggle Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        set_dark_mode(st.session_state.dark_mode)

    set_dark_mode(st.session_state.dark_mode)

    with st.form("user_form"):
        name = st.text_input("Your Name", value=st.session_state.user_data["name"] or "")
        age = st.number_input("Your Age", min_value=10, max_value=100, value=st.session_state.user_data["age"] or 18)
        gender = st.selectbox("Your Gender", options=["Male", "Female", "Other"], index=(["Male", "Female", "Other"].index(st.session_state.user_data["gender"]) if st.session_state.user_data["gender"] else 0))
        partner = st.selectbox("Choose Your Companion", options=["Boyfriend", "Girlfriend", "Friend"], index=(["Boyfriend", "Girlfriend", "Friend"].index(st.session_state.user_data["partner"]) if st.session_state.user_data["partner"] else 0))
        submitted = st.form_submit_button("💬 Start Chat")

    if submitted:
        if not name or not age or not gender or not partner:
            st.warning("❗ Please fill out all fields.")
        else:
            st.session_state.user_data.update({
                "name": name,
                "age": age,
                "gender": gender,
                "partner": partner,
                "history": []
            })
            st.success(f"✅ Hi {name}! You're now chatting with your virtual {partner}. Start by telling them how you feel today. 💬")

    if st.session_state.user_data["name"]:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        message = st.text_input("Tell me what's on your mind... 💭", key="chat_input")
        if st.button("Send") and message.strip() != "":
            response_placeholder = st.empty()
            full_response = ""
            for partial in lw_streaming_app(message, st.session_state.user_data["history"]):
                full_response = partial
                response_placeholder.markdown(f"<div class='chat-bubble-ai'>{partial}</div>", unsafe_allow_html=True)
            st.session_state.chat_history.append(("You", message))
            st.session_state.chat_history.append(("AI", full_response))

        chat_container = st.container()
        with chat_container:
            st.markdown("<div class='chat-history'>", unsafe_allow_html=True)
            for speaker, text in st.session_state.chat_history:
                if speaker == "You":
                    st.markdown(f"<div class='chat-bubble-user'>{text}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble-ai'>{text}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
