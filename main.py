import config as CFG
from utils.context_manager import ContextManager
from utils.logger import Logger
from utils.token_counter import TokenCounter
from llm_client.gemini_client import GeminiClient
from llm_client.groq_client import GroqClient
from llm_client.cohere_client import CohereClient
from llm_client.hf_client import HFClient


# Default init
context = ContextManager()
logger = Logger()
counter = TokenCounter()
current_provider = CFG.DEFAULT_PROVIDER
current_persona = CFG.DEFAULT_PERSONA
client = GeminiClient()

state = {
    'client': GeminiClient(),
    'provider': CFG.DEFAULT_PROVIDER,
    'persona': "Expert",
    'session_id': logger.session_id
}

def handle_commands(user_input, context_manager, logger, current_state):
    # current_state is dict {client, provider, persona}
    # /switch gemini -> cmd='/switch', arg='gemini'
    parts = user_input.lower().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None
    
    # /switch command
    if cmd == "/switch":
        if arg in [CFG.GEMINI_PV.lower(), 'gemini']:
            current_state['client'] = GeminiClient()
            current_state['provider'] = CFG.GEMINI_PV
            print(" == Switch to GEMINI ===")
        elif arg in [CFG.GROQ_PV.lower(), 'groq']:
            current_state['client'] = GroqClient()
            current_state['provider'] = CFG.GROQ_PV
            print(" == Switch to GROQ ===")
        elif arg in [CFG.COHERE_PV.lower(), 'cohere']:
            current_state['client'] = CohereClient()
            current_state['provider'] = CFG.COHERE_PV
            print(" == Switch to COHERE ===")
        elif arg in [CFG.HF_PV.lower(), 'hf']:
            current_state['client'] = HFClient()
            current_state['provider'] = CFG.HF_PV
            print(" == Switch to HUGGING FACE ===")
        else:
            print(f"Provider '{arg} is not valid'")
    # /persona command
    elif cmd == "/persona":
        valid_persona = ["expert", "eli5", "socratic"]
        if arg in valid_persona:
            current_persona['persona'] = arg.capitalize()
            print(f"=== Persona changed to {arg.capitalize()}")
        else:
            print(f"Persona is not valid")
            
    # /stats command
    elif cmd == "/stats":
        stats = logger.get_session_stats()
        print("\n SESSION STATISTICS")
        for key, value in stats.items():
            print(f"{key:20}: {value}")
    
    # /export command
    elif cmd == "/export":
        filename = arg if arg else f"export_{current_state['session_id']}.md"
        filepath = f"exports/{filename}"
        context_manager.export_to_markdown(filepath)
        print(f"Conversation exported to {filepath}")
    
    # /clear command
    elif cmd == "/clear":
        context_manager.clear()
        print("History cleared!")
        
    # 6. /help command
    elif cmd == "/help":
        print_help()
        
    else:
        print(f"Unknown command: {cmd}. Type /help for list of commands.")

def print_help():
    print("=== COMMAND LISTS ===")
    print("\n/switch name_client | client: gemini, groq, cohere, hf")
    print("\n/persona name_persona | persona: expert, eli5, socratic")
    print("\n/stats | session statitis")
    print("\n/export | export session")
    print("\n/clear | clear history")

try:
    while True:
        user_input = input(f"You [{state['provider']}/{state['persona']}] > ").strip()
        
        if not user_input:
            continue
        
        # command handling
        if user_input.startswith("/"):
            if user_input in ["/quit", "exit"]:
                print("Goodbye")
                break
            handle_commands(user_input) 
            continue
        
        #
except Exception as e:
    raise e