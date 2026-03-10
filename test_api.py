import os
import io
from PIL import Image
from google import genai
from google.genai import types

def test():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY")
        return
    client = genai.Client(api_key=api_key)
    
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    prompt = "Translate text from Italian to English"
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-image-preview',
            contents=[img, prompt]
        )
        print("GENERATE CONTENT SUCCESS!")
        print(response)
    except Exception as e:
        print(f"GENERATE CONTENT ERROR: {e}")

if __name__ == "__main__":
    test()
