# main.py
from llm_client.ollama_client import OLClient

def main():
    # Khởi tạo nhân viên Gemini
    client = OLClient()
    
    # Chuẩn bị câu hỏi
    system_prompt = "Bạn là một giảng viên toán."
    messages = [
        {"role": "user", "content": "Viết cho tôi bảng cửu chương 2"}
    ]
    
    # Ra lệnh (Hàm chat() này nằm ở lớp Base, nó sẽ tự gọi _call_api của Gemini)
    response = client.chat(system_prompt, messages)
    
    # In kết quả cực kỳ chuyên nghiệp từ ChatResponse
    print(f"=== {response.provider.upper()} RESPONSE ===")
    print(f"Content: {response.content}")
    print(f"Tokens: {response.total_tokens} (In: {response.input_tokens}, Out: {response.output_tokens})")
    print(f"Time: {response.latency_ms:.2f}ms")

if __name__ == "__main__":
    main()