import os
import openai
from dotenv import load_dotenv

def test_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file.")
        return

    print(f"Checking key: {api_key[:8]}...{api_key[-4:]}")
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        # Try a simple models list check (usually doesn't cost money, but checks validity)
        print("1. Checking key validity (Listing models)...")
        client.models.list()
        print("SUCCESS: Key is valid.")
        
        # Try a tiny completion check (checks quota)
        print("2. Checking quota (Generating 1 word)...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "say hi"}],
            max_tokens=5
        )
        print(f"SUCCESS: Quota is available. Response: {response.choices[0].message.content}")
        
    except openai.AuthenticationError:
        print("ERROR: Authentication failed. The key is incorrect.")
    except openai.RateLimitError as e:
        if "insufficient_quota" in str(e):
             print("ERROR: Insufficient Quota. You need to add billing/credits to your OpenAI account.")
        else:
             print(f"ERROR: Rate limit hit: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_key()
