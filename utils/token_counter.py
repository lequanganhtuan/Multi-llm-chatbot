import config as CFG
from transformers import AutoTokenizer
import tiktoken

class TokenCounter():
    def __init__(self):
        self.tokenizers = {}
    
    def get_tokenizer(self, modelName):
        if modelName in self.tokenizers:
            return self.tokenizers[modelName]
        tokenizer = None
        
        # Check the model name to get the corresponding tokenizer.
        if modelName == CFG.GEMINI_MODEL:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        elif modelName == CFG.GROQ_MODEL:
            tokenizer = AutoTokenizer.from_pretrained(modelName)
        elif modelName == CFG.COHERE_MODEL:
            tokenizer = AutoTokenizer.from_pretrained("CohereLabs/c4ai-command-r7b-12-2024")
        elif modelName == CFG.HF_MODEL:
            tokenizer = AutoTokenizer.from_pretrained(modelName)
        else:
            raise ValueError("Unsupported model")
        self.tokenizers[modelName] = tokenizer
        return tokenizer