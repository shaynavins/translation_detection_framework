from openai import OpenAI

class LLMClient:
    def __init__(self, api_key, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {'role': 'system', "content": system_prompt},
                {"role": "user", "content": user_prompt}

            ],

            temperature =0
        )

        return response.choices[0].message.content

