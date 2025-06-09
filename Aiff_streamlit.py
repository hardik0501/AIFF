import streamlit as st
from openai import OpenAI
import time

# Gemini API setup
gemini_llm_model = OpenAI(
    api_key="AIzaSyBhpRkOnmcurInRavgzB2nc0UkLulq7yYo",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Initialize session state
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": None,
        "age": None,
        "gender": None,
        "partner": None,
        "history": []
    }

# Personality presets
personalities = {
    "Boyfriend": "You are a charming, flirty, and supportive virtual boyfriend who knows how to make the user smile and feel special.",
    "Girlfriend": "You are an emotional, loving, and caring virtual girlfriend who always supports and comforts the user.",
    "Friend": "You are a chill, funny, and understanding virtual friend who listens, jokes, and gives good advice."
}

# Dark mode toggle using CSS injection
def set_dark_mode(dark):
    if dark:
        st.markdown(
            """
            <style>
            body {
                background: #121212;
                color: #eee;
                transition: background-color 0.5s ease, color 0.5s ease;
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
                background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
                color: #eee;
                transition: background-color 0.5s ease, color 0.5s ease;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

# Chat function with personality-based prompt and streaming response
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
                time.sleep(0.02)  # Slight delay for smooth streaming effect

        st.session_state.user_data["history"].append({"role": "user", "content": message})
        st.session_state.user_data["history"].append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        yield "⚠️ Something went wrong. Please try again."

# Main app
def main():
    st.title("🤖 AIFF: Your AI Friend Forever 💕🎧")
    st.markdown("<p style='text-align:center; font-weight:bold;'>Choose a virtual <b>Boyfriend 🫶</b>, <b>Girlfriend 💋</b>, or <b>Friend 🧑‍🤝‍🧑</b> and share your heart out 💌</p>", unsafe_allow_html=True)

    # Dark mode toggle
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    if st.button("🌙 Toggle Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        set_dark_mode(st.session_state.dark_mode)

    set_dark_mode(st.session_state.dark_mode)

    # User input form
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

    # Chat area
    if st.session_state.user_data["name"]:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        message = st.text_input("Tell me what's on your mind... 💭", key="chat_input")
        if st.button("Send") and message.strip() != "":
            # Stream response
            response_placeholder = st.empty()
            full_response = ""
            for partial in lw_streaming_app(message, st.session_state.user_data["history"]):
                full_response = partial
                response_placeholder.markdown(f"**AI:** {partial}")
            st.session_state.chat_history.append(("You", message))
            st.session_state.chat_history.append(("AI", full_response))

        # Show chat history
        for speaker, text in st.session_state.chat_history:
            if speaker == "You":
                st.markdown(f"<div style='text-align:right; padding:5px;'><b>You:</b> {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:left; padding:5px; color:#ff69b4;'><b>AI:</b> {text}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
