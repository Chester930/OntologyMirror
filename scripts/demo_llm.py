import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontologymirror.core.llm_client import LLMClient

def main():
    print("🚦 Starting LLM Client Demo (Stage 2)...")
    
    try:
        client = LLMClient()
        print(f"✅ Initialized Client with Provider: {client.provider}")
    except ValueError as e:
        print(f"❌ Initialization Failed: {e}")
        print("💡 Tip: Check your .env file or environment variables.")
        return

    print("\n🧐 Sending Test Message...")
    system_prompt = "You are a helpful assistant that outputs JSON."
    user_prompt = "Who are you?"
    
    try:
        response = client.generate(system_prompt, user_prompt)
        print(f"🤖 Response: {response}")
    except Exception as e:
        print(f"❌ Generation Failed: {e}")

if __name__ == "__main__":
    main()
