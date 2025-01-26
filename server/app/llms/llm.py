import ollama

class LLMService:
    """
    Service class for handling interactions with LLMs using static methods.
    """

    @staticmethod
    def generate_open_ai(prompt):
        """
        Generate chat using Openai models (e.g., GPT-3, GPT-4) and other models.
        This is a placeholder method for the actual API call to OpenAI.
        It allows api endpoints to be easily swapped out for different providers.
        """
        return f"GPT-4 Response: {prompt}"

    @staticmethod
    def generate_chat_ollama(prompt, model_name):
        """
        Generate chat using Ollama models (e.g., LLaMA, Falcon, Mistral, DeepSeek).
        """
        messages = [{"role": "user", "content": prompt}]
        return ollama.chat(
            model=model_name,
            messages=messages,
            options={"temperature": 0.9, "max_token": 2048},
            stream=True,
        )

    @staticmethod
    def generate_chat(model_provider, model_name, prompt):
        """
        Generate chat based on the specified model provider and model name.
        """
        # Map model providers to their respective methods
        model_handlers = {
            "openai": LLMService.generate_open_ai,
            "ollama": LLMService.generate_chat_ollama,
        }

        # Get the appropriate handler for the model provider
        handler = model_handlers.get(model_provider)
        if not handler:
            raise ValueError(f"Unsupported model provider: {model_provider}")

        # Call the handler with the prompt and model name
        return handler(prompt, model_name)