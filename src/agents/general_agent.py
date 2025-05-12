import openai

class Agent:
    def __init__(self, model="gpt-4o", api_key=None, temperature=0.0):
        self.model = model
        self.api_key = api_key or openai.api_key
        self.temperature = temperature

    def query(self, instructions, input_text):
        """
        Query the GPT model with the given instructions and input text.
        """
        response = openai.OpenAI(api_key=self.api_key).responses.create(
            model=self.model,
            instructions=instructions,
            input=input_text,
            temperature=self.temperature,
        )
        return response.output_text
