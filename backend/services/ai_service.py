import openai
from typing import Dict, Any
import os

class AIService:
    """Handle OpenAI API calls"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = "gpt-4"
    
    async def call_gpt(self, prompt: str, system_message: str = None) -> str:
        """Make API call to GPT-4"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling GPT: {e}")
            return ""
