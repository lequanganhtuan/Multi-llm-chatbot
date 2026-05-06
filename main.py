import config as CFG
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

from utils.context_manager import ContextManager
from utils.logger import Logger
from utils.token_counter import TokenCounter
from llm_client.gemini_client import GeminiClient
from llm_client.groq_client import GroqClient
from llm_client.cohere_client import CohereClient
from llm_client.hf_client import HFClient
from prompts.templates import get_system_prompt, get_persona_description
from prompts.few_shot_examples import get_few_shot_examples
from prompts.templates import PersonaType

# --- UI RENDERERS ---
console = Console()

def print_help():
    table = Table(title="COMMAND LIST", border_style="blue")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    table.add_row("/switch name_client", "Clients: gemini, groq, cohere, hf")
    table.add_row("/persona name_persona", "Personas: expert, eli5, socratic")
    table.add_row("/stats", "Show session statistics")
    table.add_row("/export", "Export session to markdown")
    table.add_row("/clear", "Clear chat history")
    console.print(table)

# --- LOGIC INIT (KEEP UNTOUCHED) ---
context = ContextManager()
logger = Logger()
counter = TokenCounter()
current_provider = CFG.DEFAULT_PROVIDER
current_persona = CFG.DEFAULT_PERSONA
client = GeminiClient()

state = {
    'client': GeminiClient(),
    'provider': CFG.DEFAULT_PROVIDER,
    'persona': PersonaType.EXPERT ,
    'session_id': logger.session_id,
    'model_name': CFG.GEMINI_MODEL
}

def handle_commands(user_input, context_manager, logger, state):
    parts = user_input.lower().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None
    
    if cmd == "/switch":
        if arg in [CFG.GEMINI_PV.lower(), 'gemini']:
            state['client'] = GeminiClient()
            state['provider'] = CFG.GEMINI_PV
            state['model_name'] = CFG.GEMINI_MODEL
            rprint("[bold green] == Switch to GEMINI ===[/bold green]")
        elif arg in [CFG.GROQ_PV.lower(), 'groq']:
            state['client'] = GroqClient()
            state['provider'] = CFG.GROQ_PV
            state['model_name'] = CFG.GROQ_MODEL
            rprint("[bold green] == Switch to GROQ ===[/bold green]")
        elif arg in [CFG.COHERE_PV.lower(), 'cohere']:
            state['client'] = CohereClient()
            state['provider'] = CFG.COHERE_PV
            state['model_name'] = CFG.COHERE_MODEL
            rprint("[bold green] == Switch to COHERE ===[/bold green]")
        elif arg in [CFG.HF_PV.lower(), 'hf']:
            state['client'] = HFClient()
            state['provider'] = CFG.HF_PV
            state['model_name'] = CFG.HF_MODEL
            rprint("[bold green] == Switch to HUGGING FACE ===[/bold green]")
        else:
            rprint(f"[red]Provider '{arg}' is not valid[/red]")
    elif cmd == "/persona":
        if arg == "expert":
            state['persona'] = PersonaType.EXPERT
        elif arg == "eli5":
            state['persona'] = PersonaType.ELI5
        elif arg == "socratic":
            state['persona'] = PersonaType.SOCRATIC
        rprint(f"[bold yellow]Persona changed to: {state['persona']}[/bold yellow]")
            
    elif cmd == "/stats":
        stats = logger.get_session_stats()
        rprint("\n[bold cyan] SESSION STATISTICS[/bold cyan]")
        for key, value in stats.items():
            rprint(f"{key:20}: {value}")
    
    elif cmd == "/export":
        filename = arg if arg else f"export_{state['session_id']}.md"
        filepath = f"exports/{filename}"
        context_manager.export_to_markdown(filepath)
        rprint(f"[green]Conversation exported to {filepath}[/green]")
    
    elif cmd == "/clear":
        context_manager.clear()
        rprint("[bold red]History cleared![/bold red]")
        
    elif cmd == "/help":
        print_help()
    else:
        rprint(f"[red]Unknown command: {cmd}. Type /help for list of commands.[/red]")

# --- MAIN LOOP ---
try:
    rprint(Panel("[bold magenta]MULTI-LLM CHATBOT READY[/bold magenta]", border_style="cyan"))
    while True:
        # Thay input() bằng console.input() để có màu sắc
        prompt_str = f"[bold green]You [{state['provider']}/{state['persona']}][/bold green] > "
        user_input = console.input(prompt_str).strip()
        
        if not user_input:
            continue
        
        if user_input.startswith("/"):
            if user_input in ["/quit", "exit"]:
                rprint("[bold red]Goodbye[/bold red]")
                break
            handle_commands(user_input, context, logger, state) 
            continue
        
        # --- ORIGINAL LOGIC (UNTOUCHED) ---
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
        
        token_usage = counter.get_usage_report(messages_for_token, state['model_name'])
        
        # Chỉ thay print bằng rprint/console để đẹp hơn
        rprint(f"[blue]Current Token:[/blue] {token_usage['current']}")
        rprint(f"[blue]Max token:[/blue] {token_usage['max']}")
        rprint(f"[blue]Percentage usage:[/blue] {token_usage['percentage']}")
        rprint(f"[blue]Status:[/blue] {token_usage['tag']} / [blue]overflow[/blue] {token_usage['is_overflow']}")
        
        if token_usage["is_overflow"]:
            rprint("[bold red]⚠️ Context overflow! Consider clearing history.[/bold red]")
            continue
                
        rprint("[dim]==== DEBUG MESSAGES ====[/dim]")
        for i, m in enumerate(messages_for_api):
            content = m.get("content", "")
            rprint(f"[dim][{i}] role={m.get('role')} | length={len(content)}[/dim]")
            if not content.strip():
                rprint("    [bold red]❌ EMPTY CONTENT DETECTED![/bold red]")
        
        rprint(f"[dim]SYSTEM PROMPT: {repr(system_prompt)}[/dim]")
        rprint("[dim]========================[/dim]")
                
        client = state['client']
        
        # API Call với Spinner cho đẹp
        with console.status("[bold green]Processing...", spinner="dots"):
            response = client.chat(
                system_prompt=system_prompt,
                messages=messages_for_api
            )
        
        # In kết quả trong Panel
        console.print(Panel(
            response.content, 
            title=f"[bold cyan]{state['provider']} ({state['persona']})[/bold cyan]",
            title_align="left",
            border_style="magenta"
        ))
        
        rprint(f"[italic]Tokens: {response.total_tokens} | ⏱ {response.latency_ms}ms[/italic]")

        context.add_turn(
            user_msg=user_input,
            assistant_msg=response.content,
            metadata={
                "provider": state['provider'],
                "persona": state['persona'],
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "latency_ms": response.latency_ms
            }
        )

        logger.log_request(
            response=response,
            provider=state['provider'],
            turn_id=context.current_id - 1,
            persona=state['persona'],
            model_name=state['model_name']
        )
                
except Exception as e:
    console.print_exception() # In lỗi đẹp mắt thay vì raise e thô kệch