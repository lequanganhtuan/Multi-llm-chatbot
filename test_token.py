import config as CFG
from utils.token_counter import TokenCounter

def test_counter():
    counter = TokenCounter()
    
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    
    models_to_test = [CFG.GEMINI_MODEL, CFG.GROQ_MODEL, CFG.COHERE_MODEL, CFG.HF_MODEL]
    
    for model in models_to_test:
        print(f"\n--- Testing Model: {model} ---")
        
        count = counter.count_messages_tokens(test_messages, model)
        print(f"Total Tokens: {count}")
        
        report = counter.get_usage_report(test_messages, model)
        print(f"Report String: {report['report_str']}")
        print(f"Is Overflow: {report['is_overflow']}")

if __name__ == "__main__":
    test_counter()