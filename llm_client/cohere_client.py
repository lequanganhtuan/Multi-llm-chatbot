from .base_client import BaseLLMClient
import config as CFG
import cohere

class CohereClient(BaseLLMClient):
    
    def __init__(self):
        super().__init__(
            api_key = CFG.COHERE_API_KEY,
            model_name = CFG.COHERE_MODEL,
            provider = 'Cohere',
            context_limit = CFG.COHERE_CONTEXT_LIMIT,
        )
        
        self.client = cohere.Client(api_key=self.api_key)
        
    def _call_api(self, system_prompt, messages):
        try:
            #split last message in history
            last_message_content = messages[-1]['content']
            
            cohere_history = []
            #change format except the last 
            for m in messages[:-1]:
                new_role = 'CHATBOT' if m['role'] == 'assistant' else 'USER'
                    
                cohere_history.append({
                    "role": new_role,
                    "message": m['content']
                })
                
            
            response = self.client.chat(
                model=self.model_name,
                message=last_message_content, 
                chat_history=cohere_history, 
                preamble=system_prompt        
            )
            
            return {
                "content": response.text,
                "input_tokens": response.meta.tokens.input_tokens,
                "output_tokens": response.meta.tokens.output_tokens   
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
                clean_error = "API Error: Cohere server is having issues. Please try again later."
            else:
                clean_error = f"API Error: An unexpected error occurred: {error_msg}"
            
            return {
                "content": clean_error,
                "input_tokens": 0,
                "output_tokens": 0
            }