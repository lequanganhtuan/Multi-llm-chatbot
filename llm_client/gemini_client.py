from .base_client import BaseLLMClient
import config as CFG
import google.generativeai as genai

class GeminiClient(BaseLLMClient):
    
    def __init__(self):
        super().__init__(
            api_key = CFG.GEMINI_API_KEY,
            model_name = CFG.GEMINI_MODEL,
            provider = CFG.GEMINI_PV,
            context_limit = CFG.GEMINI_CONTEXT_LIMIT,
        )
        
        # connect api key
        genai.configure(api_key=self.api_key)
        
    
    def _call_api(self, system_prompt, messages):
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,        
                system_instruction=system_prompt  
            )
            
            gemini_history = []
            
            # Format messages
            for m in messages:
                role = 'model' if m['role'] == 'assistant' else m['role']
                    
                gemini_history.append({
                    "role": role,
                    "parts": [m['content']]
                })
                
            
            response = model.generate_content(gemini_history)
            
            return {
                "content": response.text,
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count
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
                clean_error = "API Error: Google server is having issues. Please try again later."
            else:
                clean_error = f"API Error: An unexpected error occurred: {error_msg}"
            
            return {
                "content": clean_error,
                "input_tokens": 0,
                "output_tokens": 0
            }