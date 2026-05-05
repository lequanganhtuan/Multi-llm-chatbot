from .base_client import BaseLLMClient
import config as CFG
from huggingface_hub import InferenceClient

class HFClient(BaseLLMClient):
    
    def __init__(self):
        super().__init__(
            api_key = CFG.HF_TOKEN,
            model_name = CFG.HF_MODEL,
            provider = CFG.HF_PV,
            context_limit = CFG.HF_CONTEXT_LIMIT,
        )
        
        self.client = InferenceClient(api_key=self.api_key)
        
    def _call_api(self, system_prompt, messages):
        try:
            hf_messages = [{"role": "system", "content": system_prompt}]
            for m in messages:
                hf_messages.append({"role": m['role'], "content": m['content']})
                        
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=hf_messages,
                max_tokens=getattr(CFG, 'MAX_TOKENS', 512)
            )
            
            return {
                "content": response.choices[0].message.content,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                clean_error = "API Error: Quota exceeded. Please wait a moment before retrying."
            elif "403" in error_msg or "PermissionDenied" in error_msg:
                clean_error = "API Error: Invalid API Key or permission denied."
            elif "404" in error_msg or "NotFound" in error_msg:
                clean_error = f"API Error: Model '{self.model_name}' not found."
            elif "500" in error_msg:
                clean_error = "API Error: Groq server is having issues. Please try again later."
            else:
                clean_error = f"API Error: An unexpected error occurred: {error_msg}"
            
            return {
                "content": clean_error,
                "input_tokens": 0,
                "output_tokens": 0
            }