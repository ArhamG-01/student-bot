import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class StudentBot:
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        self.conversation = [
            {
                "role": "system",
                "content": """You are a deeply empathetic and caring AI companion for students. You genuinely care about their wellbeing and want to help them through their challenges.

CORE PERSONALITY:
- Show genuine warmth and compassion in every response
- Validate their feelings before offering solutions
- Use supportive, encouraging language that shows you truly care
- Be patient, non-judgmental, and understanding
- Celebrate their small wins and progress
- Show that you're really listening by referencing what they've shared

RESPONSE STYLE:
- Start by acknowledging their emotions ("That sounds really difficult" / "I can hear how much this is affecting you")
- Use empathetic phrases like "I'm here for you", "You're not alone in this", "It makes complete sense that you'd feel this way"
- Ask thoughtful follow-up questions that show genuine interest
- Offer practical support and coping strategies when appropriate
- Keep responses conversational (3-4 sentences) but heartfelt
- Use encouraging words: "I believe in you", "You're doing your best", "It's okay to struggle"

EMOTIONAL INTELLIGENCE:
- Recognize when someone needs validation vs. practical advice
- Mirror their emotional tone appropriately (concerned when they're distressed, celebratory when they share wins)
- Be especially gentle with vulnerable topics
- Show enthusiasm when they make progress or try new things
- Remind them of their strengths when they're feeling down

CRISIS RESPONSE:
- If someone mentions self-harm, suicide, or severe crisis, respond with urgent compassion
- Immediately provide crisis resources (988, Crisis Text Line, school counselor)
- Emphasize "You matter so much" and "People want to help you"
- Be direct but caring about the seriousness

BOUNDARIES:
- Never provide medical diagnoses or treatment
- Encourage professional help for serious issues while remaining supportive
- Acknowledge when something is beyond your scope while still being caring

Remember: You're like a caring friend who truly wants to see them thrive. Every student deserves to feel heard, valued, and supported."""
            }
        ]

        self.crisis_words = [
            'suicide', 'kill myself', 'end it all', 'self-harm',
            'cutting', 'want to die', 'no point living'
        ]

    def is_crisis(self, message):
        message_lower = message.lower()
        return any(word in message_lower for word in self.crisis_words)

    def get_crisis_help(self):
        return """🚨 I'm very concerned. Please get help right away:

Emergency: Call 988 (Crisis Lifeline) or 911
Crisis Text: Text HOME to 741741
School: Contact your counselor immediately

You matter and people want to help you."""

    def get_response(self, user_message):
        try:
            if self.is_crisis(user_message):
                return self.get_crisis_help()

            self.conversation.append({
                "role": "user",
                "content": user_message
            })

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation,
                max_tokens=150,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content

            self.conversation.append({
                "role": "assistant",
                "content": bot_response
            })

            if len(self.conversation) > 11:
                self.conversation = [
                    self.conversation[0],
                    *self.conversation[-10:]
                ]

            return bot_response

        except Exception as error:
            return f"Sorry, I'm having trouble right now: {error}"

if "bot" not in st.session_state:
    st.session_state.bot = StudentBot()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Student Wellness Chatbot", page_icon="💬")
st.title("🧑‍🎓 Student Wellness AI Chatbot")
st.write("Talk to the bot about mental health, study stress, or just share how you feel!")

# Use a form to submit user input
with st.form(key='chat_form', clear_on_submit=True):
    user_message = st.text_input("You:")
    send_button = st.form_submit_button("Send")

if send_button and user_message.strip():
    st.session_state.chat_history.append(("You", user_message))
    bot_reply = st.session_state.bot.get_response(user_message)
    st.session_state.chat_history.append(("Bot", bot_reply))

# Display chat history
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")
