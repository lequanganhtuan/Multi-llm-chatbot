import config as CFG
import uuid
import os
import csv
from datetime import datetime
import pandas as pd

class Logger:
    cost_table = {
        CFG.GEMINI_PV: {"input": 0.35, "output": 1.05},
        CFG.GROQ_PV: {"input": 0.05, "output": 0.10},
        CFG.COHERE_PV: {"input": 0.5, "output": 1.5},
        CFG.HF_PV: {"input": 0.2, "output": 0.2}
    }

    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        os.makedirs("logs", exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"logs/session_{timestamp_str}_{self.session_id}.csv"
        
        self.fieldnames = [
            "timestamp", "session_id", "turn_id", "provider", "model", 
            "persona", "input_tokens", "output_tokens", "total_tokens", 
            "latency", "cost", "text"
        ]

    def calculate_cost(self, input_tokens, output_tokens, provider) -> float:
        prices = self.cost_table.get(provider, {"input": 0, "output": 0})
        
        cost_input = (input_tokens / 1_000_000) * prices["input"]
        cost_output = (output_tokens / 1_000_000) * prices["output"]

        return round(cost_input + cost_output, 6)
    
    def log_request(self, response, provider, turn_id, persona, model_name):
        cost = self.calculate_cost(
            response.input_tokens,
            response.output_tokens,
            provider
        )

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.session_id,
            "turn_id": turn_id,
            "provider": provider,
            "model": model_name,
            "persona": persona,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "total_tokens": response.input_tokens + response.output_tokens,
            "latency": response.latency,
            "cost": cost,
            "text": response.text[:100].replace("\n", " ")
        }

        file_exists = os.path.isfile(self.filename)

        with open(self.filename, mode="a", newline="", encoding="utf-8") as f:
            # Dùng fieldnames cố định
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def get_session_stats(self):
        try:
            df = pd.read_csv(self.filename)
            if df.empty:
                return {"message": "No data"}

            stats = {
                "total_requests": len(df),
                "total_tokens": int(df["total_tokens"].sum()),
                "total_cost": round(df["cost"].sum(), 6),
                "avg_latency": round(df["latency"].mean(), 2)
            }
            return stats
        except Exception:
            return {"error": "Could not read log file"}