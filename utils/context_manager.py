from dataclasses import dataclass
from datetime import datetime
from collections import deque
import config as CFG
from collections import Counter


@dataclass
class ConversationTurn:
    turn_id: str
    user_message: str
    assistant_message: str
    provider: str
    persona: str
    timestamp: datetime
    input_tokens: int
    output_tokens: int
    latency_ms: float
    
class ContextManager:
    def __init__(self):
        self.sliding_window = deque(maxlen=CFG.MAX_HISTORY_TURNS)
        self.full_history = []
        self.current_id = 1
        
    def get_messages(self):
        messages = []
    
        for turn in self.sliding_window:
            messages.append({
                "role": "user",
                "content": turn.user_message
            })
            
            messages.append({
                "role": "assistant",
                "content": turn.assistant_message
            })
        
        return messages
    
    def add_turn(self, user_msg: str, assistant_msg: str, metadata: dict):
        results = ConversationTurn(
            turn_id=self.current_id,
            user_message= user_msg,
            assistant_message= assistant_msg,
            provider= metadata.get('provider', 'unknown'),
            persona=metadata.get('persona', 'Default'),
            timestamp = datetime.now(),
            input_tokens=metadata.get('input_tokens', 0),
            output_tokens=metadata.get('output_tokens', 0),
            latency_ms=metadata.get('latency_ms', 0.0)
        )
        
        self.current_id += 1
        
        self.full_history.append(results)
        self.sliding_window.append(results)
        
    def get_full_history(self):
        return self.full_history

    def clear(self):
        self.sliding_window.clear()
        self.full_history.clear()
        self.current_id = 1

    def get_stats(self):
        if not self.full_history:
            return {"total_turns": 0, "total_tokens": 0}
            
        total_in = sum(h.input_tokens for h in self.full_history)
        total_out = sum(h.output_tokens for h in self.full_history)
        total_latency = sum(h.latency_ms for h in self.full_history)
        
        providers = Counter(h.provider for h in self.full_history)
        
        return {
            "total_turns": len(self.full_history),
            "total_input_tokens": total_in,
            "total_output_tokens": total_out,
            "avg_latency": total_latency / len(self.full_history),
            "providers": dict(providers)
        }

    def export_to_markdown(self, filepath: str):
        stats = self.get_stats()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Conversation Export\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Turns:** {stats['total_turns']}\n\n---\n")
            
            for turn in self.full_history:
                f.write(f"## Turn {turn.turn_id}\n")
                f.write(f"**User:** {turn.user_message}\n\n")
                f.write(f"**Assistant ({turn.provider} | {turn.persona}):** {turn.assistant_message}\n\n")
                f.write(f"*Tokens: {turn.input_tokens} in / {turn.output_tokens} out | Latency: {turn.latency_ms}ms*\n\n---\n")
            
            # 3. Ghi Stats cuối file
            f.write("\n## Stats\n")
            f.write(f"- Total input tokens: {stats['total_input_tokens']}\n")
            f.write(f"- Total output tokens: {stats['total_output_tokens']}\n")
            
            total_turn_tokens = turn.input_tokens + turn.output_tokens
            f.write(f"*Tokens: {turn.input_tokens} in / {turn.output_tokens} out (Total: {total_turn_tokens}) | Latency: {turn.latency_ms}ms*\n\n---\n")