import os
from dotenv import load_dotenv

def run_test():
    load_dotenv(override=True)
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print('No API key found in environment variables')
        return

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model='gemini-3.6-flash')
        response = chat.send_message('Say "Hello World!"')
        print('SUCCESS:', response.text)
    except Exception as e:
        print('ERROR:', str(e))

if __name__ == "__main__":
    run_test()
