import gradio as gr
from openai import OpenAI

# Gemini API setup
gemini_llm_model = OpenAI(
    api_key="Put your api here",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

user_data = {
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

# Chat function with personality-based prompt
def lw_streaming_app(message, history):
    try:
        role_prompt = personalities.get(user_data['partner'], "You are a supportive AI friend.")
        system_prompt = {
            "role": "system",
            "content": f"{role_prompt} The user is a {user_data['age']}-year-old {user_data['gender']} named {user_data['name']}."
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

        user_data["history"].append({"role": "user", "content": message})
        user_data["history"].append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        print("Chat Error:", e)
        yield "⚠️ Something went wrong. Please try again."

# User intro handler
def start_chat(name, age, gender, partner):
    if not name or not age or not gender or not partner:
        return "❗ Please fill out all fields."
    user_data["name"] = name
    user_data["age"] = age
    user_data["gender"] = gender
    user_data["partner"] = partner
    user_data["history"] = []
    return f"✅ Hi {name}! You're now chatting with your virtual {partner}. Start by telling them how you feel today. 💬"

# JS for dark mode toggle: toggles 'dark' class on body and returns new button text
toggle_dark_mode_js = """
const body = document.body;
body.classList.toggle('dark');
if(body.classList.contains('dark')) {
    return '☀️ Light Mode';
} else {
    return '🌙 Dark Mode';
}
"""

css = """
:root {
    --bg-light: #f0f4f8;
    --bg-dark: #121212;
    --primary: #ff69b4;
    --secondary: #f48fb1;
    --text-light: #222;
    --text-dark: #eee;
}

body {
    margin: 0; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
    color: var(--text-dark);
    transition: background-color 0.5s ease, color 0.5s ease;
}

body.dark {
    background: var(--bg-dark);
    color: var(--text-light);
}

#dark-mode-toggle {
    position: fixed;
    top: 15px;
    right: 15px;
    background: var(--primary);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 30px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgb(255 105 180 / 0.7);
    transition: background-color 0.3s ease;
    z-index: 1000;
}

#dark-mode-toggle:hover {
    background: var(--secondary);
}

.gradio-container {
    max-width: 720px;
    margin: 80px auto 40px;
    padding: 30px 30px 40px;
    background: rgba(255 255 255 / 0.12);
    border-radius: 20px;
    box-shadow: 0 8px 30px rgb(0 0 0 / 0.15);
    transition: background 0.5s ease;
}

body.dark .gradio-container {
    background: rgba(255 255 255 / 0.05);
}

.gr-chatbot {
    border-radius: 15px !important;
    box-shadow: 0 8px 20px rgb(255 105 180 / 0.3) !important;
}

.gr-button {
    background-color: var(--primary) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 30px !important;
    padding: 12px 30px !important;
    box-shadow: 0 5px 15px rgb(255 105 180 / 0.7) !important;
    transition: background-color 0.3s ease !important;
}

.gr-button:hover {
    background-color: var(--secondary) !important;
}

h1, h2, h3, p {
    text-align: center;
    font-weight: 700;
}

.emoji-animate {
    display: inline-block;
    animation: bounce 1.5s ease-in-out infinite;
    transform-origin: center bottom;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
"""

with gr.Blocks(css=css) as demo:

    # Dark mode toggle button
    dark_mode_btn = gr.Button("🌙 Dark Mode", elem_id="dark-mode-toggle")

    # Header with animated emojis
    gr.Markdown("""
    <h1>🤖 <span class='emoji-animate'>AIFF</span>: Your AI Friend Forever <span class='emoji-animate'>💕</span></h1>
    <p>Choose a virtual <b>Boyfriend 🫶</b>, <b>Girlfriend 💋</b>, or <b>Friend 🧑‍🤝‍🧑</b> and share your heart out 💌</p>
    """)

    with gr.Accordion("📝 Fill your details", open=True):
        name = gr.Textbox(label="Your Name", placeholder="Type your name here")
        age = gr.Number(label="Your Age", minimum=10, maximum=100)
        gender = gr.Dropdown(["Male", "Female", "Other"], label="Your Gender")
        partner = gr.Dropdown(["Boyfriend", "Girlfriend", "Friend"], label="Choose Your Companion")
        intro_btn = gr.Button("💬 Start Chat")
        intro_output = gr.Textbox(label="Intro Message", interactive=False)

    intro_btn.click(start_chat, inputs=[name, age, gender, partner], outputs=intro_output)

    with gr.Column(visible=False) as chat_section:
        chat_interface = gr.ChatInterface(
            fn=lw_streaming_app,
            title="💬 Your AI Companion",
            chatbot=gr.Chatbot(label="AI Partner 💕", type="messages"),
            textbox=gr.Textbox(placeholder="Tell me what's on your mind... 💭"),
            type="messages"
        )

    def show_chat(_): 
        return gr.update(visible=True)

    intro_btn.click(fn=show_chat, inputs=intro_output, outputs=chat_section)

    # Dark mode toggle callback (run JS to toggle body class and update button text)
    dark_mode_btn.click(
        lambda: gr.JS(toggle_dark_mode_js),
        inputs=None,
        outputs=dark_mode_btn
    )

demo.launch()
