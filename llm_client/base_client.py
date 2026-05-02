from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import time
import config as CFG

# Outputs form
@dataclass
class ChatResponse:
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    model: str
    provider: str

class BaseLLMClient(ABC):
    def __init__(self, api_key, model_name, provider, context_limit):
        self.api_key = api_key
        self.model_name = model_name
        self.provider = provider
        self.context_limit = context_limit
        
    @abstractmethod
    def _call_api(self, system_prompt, messages: list):
        pass
    
    
    def chat(self, system_prompt, messages):
        start_time = time.perf_counter() #start counter
        
        for retry in range(CFG.MAX_RETRIES): #retry call api to get result and return form response from API and calculate time if error raise error
            try:
                result = self._call_api(system_prompt, messages)
                latency = (time.perf_counter() - start_time) * 1000
                return ChatResponse(
                    content=result['content'],
                    input_tokens=result['input_tokens'],
                    output_tokens=result['output_tokens'],
                    total_tokens=result['input_tokens'] + result['output_tokens'],
                    latency_ms=latency,
                    model=self.model_name,
                    provider=self.provider
                    )
            except Exception as e:
                if (retry == CFG.MAX_RETRIES - 1):
                    raise e
                wait_time = (2 ** retry) 
                time.sleep(wait_time)
                
    