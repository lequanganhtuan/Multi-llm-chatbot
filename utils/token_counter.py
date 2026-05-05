import config as CFG
from transformers import AutoTokenizer
import tiktoken

class TokenCounter:
    def __init__(self):
        self.tokenizers = {}
    
    def get_tokenizer(self, modelName):
        if modelName in self.tokenizers:
            return self.tokenizers[modelName]
        tokenizer = None
        
        # Check the model name to get the corresponding tokenizer.
        if modelName == CFG.GEMINI_MODEL or modelName == CFG.GROQ_MODEL or modelName == CFG.COHERE_MODEL:
            tokenizer = tiktoken.get_encoding("cl100k_base")
            
        elif modelName == CFG.HF_MODEL:
            try:
                tokenizer = AutoTokenizer.from_pretrained(modelName)
            except Exception:
                tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            raise ValueError("Unsupported model")
        self.tokenizers[modelName] = tokenizer
        return tokenizer
    
    def count_messages_tokens(self, messages, modelName):
        tokenizer = self.get_tokenizer(modelName)
        
        total_tokens = 0
        
        for m in messages:
            total_tokens += 4
            content = m.get("content", "")
            
            if "tiktoken" in str(type(tokenizer)):
                num_tokens = len(tokenizer.encode(content))
            else:
                num_tokens = len(tokenizer.encode(content, add_special_tokens=False))
        
            total_tokens += num_tokens
            
        total_tokens += 3    
        
        return total_tokens
    
    def get_usage_report(self, messages, model_name):
        max_tokens = 0
        
        if (model_name == CFG.GEMINI_MODEL):
            max_tokens = CFG.GEMINI_CONTEXT_LIMIT
        elif (model_name == CFG.GROQ_MODEL):
            max_tokens = CFG.GROQ_CONTEXT_LIMIT
        elif (model_name == CFG.COHERE_MODEL): 
            max_tokens = CFG.COHERE_CONTEXT_LIMIT
        else:
            max_tokens = CFG.HF_CONTEXT_LIMIT
            
        current_tokens = self.count_messages_tokens(messages, model_name)
        
        percentage = current_tokens / max_tokens
        if percentage > 0.9:
            tag = "CRITICAL"
        elif percentage > 0.7:
            tag = "WARNING"
        else:
            tag = "OK"
            
        is_overflow = True if (current_tokens > max_tokens) else False 
        
        return {
            "current": current_tokens,
            "max": max_tokens,
            "percentage": f"{percentage:.2%}",
            "tag": tag,
            "is_overflow": is_overflow,
            "report_str": f"Tokens: {current_tokens:,} / {max_tokens:,} ({percentage:.2%}) [{tag}]"
        }
        

        
            