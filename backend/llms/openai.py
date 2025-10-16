import os
from langchain_openai import ChatOpenAI
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from the .env file into the system environment
load_dotenv()

# Retrieve API credentials and configuration details from environment variables
# OpenAI API key for authentication
openai_api_key = os.getenv("OPENAI_API_KEY")
# Model name (e.g., "gpt-4-turbo", "gpt-3.5-turbo", etc.)
openai_model_name = os.getenv("OPENAI_MODEL")
# Optional base URL for OpenRouter or other gateways
base_url = os.getenv("OPEN_ROUTER_BASE_URL")


@dataclass
class OpenAIChatConfig:
    """
    Data class for storing OpenAI Chat model configuration.
    This helps maintain clean and type-safe configuration management.
    """
    model: str = openai_model_name                     # Default model name
    api_key: str = openai_api_key                      # OpenAI API key
    # Base URL for API (optional)
    base_url: str = base_url
    # Controls randomness in model responses
    temperature: float = 0.3


def OpenAIChatModel(config: OpenAIChatConfig):
    """
    Initialize and return a ChatOpenAI instance using provided configuration.

    Args:
        config (OpenAIChatConfig): Configuration object containing model parameters.

    Returns:
        ChatOpenAI: An initialized LLM client ready for interaction.
    """
    return ChatOpenAI(
        model=config.model,                            # Specify the model to use
        api_key=config.api_key,                        # API key for authentication
        base_url=config.base_url,                      # Optional custom endpoint
        # Control creativity in responses
        temperature=config.temperature,
    )
