"""
AI Model Configuration
Easy configuration for AI models used in earthquake analysis.
Add/remove/modify models here without touching the main code.
"""

# Available AI models for earthquake analysis
# Format: 'model_id': {'name': 'Display Name', 'description': 'Brief description', 'priority': order}
AI_MODELS = {
    'x-ai/grok-4-fast': {
        'name': 'Grok 4 Fast',
        'description': 'Fast and reliable AI model by xAI',
        'priority': 1,
        'max_tokens': 3000,
        'temperature': 0.7
    },
    'openai/gpt-5': {
        'name': 'GPT-5',
        'description': 'OpenAI GPT-5 - Powerful and accurate',
        'priority': 2,
        'max_tokens': 3000,
        'temperature': 0.7
    },
    'openai/gpt-oss-120b': {
        'name': 'GPT-120B',
        'description': 'OpenAI GPT-120B - Open source alternative',
        'priority': 3,
        'max_tokens': 3000,
        'temperature': 0.7
    },
    'google/gemini-2.5-flash': {
        'name': 'Gemini 2.5 Flash',
        'description': 'Google Gemini - Fast and efficient',
        'priority': 4,
        'max_tokens': 3000,
        'temperature': 0.7
    },
    'openai/gpt-4.1-mini': {
        'name': 'GPT-4.1 Mini',
        'description': 'OpenAI GPT-4.1 Mini - Fast and efficient',
        'priority': 5,
        'max_tokens': 3000,
        'temperature': 0.7
    },
    'x-ai/grok-code-fast-1': {
        'name': 'Grok Code Fast 1',
        'description': 'xAI Grok Code - Fast and efficient',
        'priority': 6,
        'max_tokens': 3000,
        'temperature': 0.7
    }
}

# Default model to use if none specified
DEFAULT_MODEL = 'x-ai/grok-4-fast'

# Fallback models to try if the selected model fails
# These will be tried in order if the primary model is unavailable
FALLBACK_MODELS = [
    'x-ai/grok-4-fast',
    'openai/gpt-5',
    'openai/gpt-oss-120b',
    'google/gemini-2.5-flash',
    'openai/gpt-4.1-mini',
    'x-ai/grok-code-fast-1'
]


def get_available_models():
    """Get list of available models sorted by priority"""
    return sorted(
        [
            {
                'id': model_id,
                **config
            }
            for model_id, config in AI_MODELS.items()
        ],
        key=lambda x: x['priority']
    )


def get_model_config(model_id):
    """Get configuration for a specific model"""
    return AI_MODELS.get(model_id, AI_MODELS[DEFAULT_MODEL])


def validate_model(model_id):
    """Check if a model ID is valid"""
    return model_id in AI_MODELS
