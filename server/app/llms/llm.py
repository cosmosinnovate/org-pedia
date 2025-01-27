import ollama
import logging

logger = logging.getLogger(__name__)

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
    def generate_chat_ollama(messages, model_name):
        """
        Generate chat using Ollama models (e.g., LLaMA, Falcon, Mistral, DeepSeek).
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            model_name (str): Name of the Ollama model to use
            
        Returns:
            generator: Stream of response chunks from the model
        """
        try:
            logger.info(f"Generating chat with {model_name}")
            return ollama.chat(
                model=model_name,
                messages=messages,
                options={"temperature": 0.9, "max_tokens": 2048},
                stream=True,
            )
        except Exception as e:
            logger.error(f"Error generating chat: {str(e)}")
            raise

    @staticmethod
    def generate_chat(model_provider, model_name, messages):
        """
        Generate chat using different model providers.
        
        Args:
            model_provider (str): Provider of the model (e.g., 'ollama', 'openai')
            model_name (str): Name of the model to use
            messages (list): List of message dictionaries with 'role' and 'content'
            
        Returns:
            generator: Stream of response chunks from the model
        """
        if model_provider == "ollama":
            return LLMService.generate_chat_ollama(messages, model_name)
        elif model_provider == "openai":
            return LLMService.generate_open_ai(messages)
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")