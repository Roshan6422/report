import requests
import json
import time

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, prompt, model="deepseek/deepseek-chat", max_tokens=4000, temperature=0.7):
        """
        Send a chat completion request to OpenRouter
        
        Args:
            prompt: The user prompt/message
            model: Model to use (default: deepseek/deepseek-chat)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        
        Returns:
            The model's response text
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenRouter API: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def list_models(self):
        """List all available models"""
        url = f"{self.base_url}/models"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing models: {e}")
            raise
    
    def translate_sinhala_to_english(self, sinhala_text, context="police report"):
        """
        Translate Sinhala text to English
        
        Args:
            sinhala_text: Sinhala text to translate
            context: Context for translation (default: "police report")
        
        Returns:
            Translated English text
        """
        prompt = f"""Translate the following Sinhala text to English. This is from a {context}.
Maintain formal tone and accuracy.

Sinhala text:
{sinhala_text}

English translation:"""
        
        return self.chat_completion(prompt, model="deepseek/deepseek-chat")

if __name__ == "__main__":
    # Test the client
    api_key = "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"
    client = OpenRouterClient(api_key)
    
    print("Testing OpenRouter Client...")
    print("=" * 60)
    
    # Test 1: Simple chat
    print("\nTest 1: Simple chat completion")
    print("-" * 60)
    response = client.chat_completion("Say 'Hello, I am working!' in one sentence.")
    print(f"Response: {response}")
    
    # Test 2: Translation test
    print("\n\nTest 2: Sinhala to English translation")
    print("-" * 60)
    sinhala_sample = "පොලිස් ස්ථානයට පැමිණි පැමිණිල්ල සම්බන්ධයෙන් විමර්ශන සිදු කරන ලදී."
    translation = client.translate_sinhala_to_english(sinhala_sample)
    print(f"Sinhala: {sinhala_sample}")
    print(f"English: {translation}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
