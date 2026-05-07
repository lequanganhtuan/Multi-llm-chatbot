import streamlit as st
import config as CFG

from utils.context_manager import ContextManager
from utils.logger import Logger
from utils.token_counter import TokenCounter

from llm_client.gemini_client import GeminiClient
from llm_client.groq_client import GroqClient
from llm_client.cohere_client import CohereClient
from llm_client.hf_client import HFClient

from prompts.templates import get_system_prompt, PersonaType
from prompts.few_shot_examples import get_few_shot_examples

# ========================
# INIT STATE (QUAN TRỌNG)
# ========================
if "context" not in st.session_state:
    st.session_state.context = ContextManager()
    st.session_state.logger = Logger()
    st.session_state.counter = TokenCounter()

    st.session_state.state = {
        'client': GeminiClient(),
        'provider': CFG.DEFAULT_PROVIDER,
        'persona': PersonaType.EXPERT,
        'model_name': CFG.GEMINI_MODEL
    }

# Shortcut
context = st.session_state.context
logger = st.session_state.logger
counter = st.session_state.counter
state = st.session_state.state

# ========================
# SIDEBAR CONTROL
# ========================
st.sidebar.title("⚙️ Settings")

provider = st.sidebar.selectbox(
    "Provider",
    ["gemini", "groq", "cohere", "hf"]
)

persona = st.sidebar.selectbox(
    "Persona",
    ["expert", "eli5", "socratic"]
)

# Update state
if provider != state["provider"]:
    if provider == "gemini":
        state["client"] = GeminiClient()
        state["model_name"] = CFG.GEMINI_MODEL
    elif provider == "groq":
        state["client"] = GroqClient()
        state["model_name"] = CFG.GROQ_MODEL
    elif provider == "cohere":
        state["client"] = CohereClient()
        state["model_name"] = CFG.COHERE_MODEL
    elif provider == "hf":
        state["client"] = HFClient()
        state["model_name"] = CFG.HF_MODEL

    state["provider"] = provider

# Persona
if persona == "expert":
    state["persona"] = PersonaType.EXPERT
elif persona == "eli5":
    state["persona"] = PersonaType.ELI5
elif persona == "socratic":
    state["persona"] = PersonaType.SOCRATIC

# ========================
# MAIN UI
# ========================
st.title("🧠 Multi-LLM Chat")

# Show history
for turn in context.sliding_window:
    with st.chat_message("user"):
        st.write(turn.user_message)
    with st.chat_message("assistant"):
        st.write(turn.assistant_message)

# ========================
# INPUT
# ========================
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # === LOGIC GIỮ NGUYÊN ===
    message_history = context.get_messages()

    system_prompt = get_system_prompt(state["persona"])
    few_shot = get_few_shot_examples(state['persona'])

    messages_for_token = []
    messages_for_token.append({"role": "system", "content": system_prompt})
    messages_for_token.extend(few_shot)
    messages_for_token.extend(message_history)
    messages_for_token.append({"role": "user", "content": user_input})

    messages_for_api = []
    messages_for_api.extend(few_shot)
    messages_for_api.extend(message_history)
    messages_for_api.append({"role": "user", "content": user_input})

    # Token usage
    token_usage = counter.get_usage_report(messages_for_token, state['model_name'])

    st.info(f"""
    Tokens: {token_usage['current']} / {token_usage['max']}  
    Usage: {token_usage['percentage']}  
    Status: {token_usage['tag']}
    """)

    if token_usage["is_overflow"]:
        st.error("⚠️ Context overflow!")
    else:
        # Call model
        with st.spinner("Thinking..."):
            response = state['client'].chat(
                system_prompt=system_prompt,
                messages=messages_for_api
            )

        # Show assistant
        with st.chat_message("assistant"):
            st.write(response.content)

        # Save
        context.add_turn(
            user_msg=user_input,
            assistant_msg=response.content,
            metadata={
                "provider": state['provider'],
                "persona": str(state['persona']),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "latency_ms": response.latency_ms
            }
        )