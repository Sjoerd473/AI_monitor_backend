# Updated to match ChatGPTDetector event structure EXACTLY

MODEL_REGISTRY = {
    # Updated with exact model names from getChatGPTModel()
    ("gpt-4o", "standard"): {
        "energy_per_input_token": 0.000002,   # Wh/token
        "energy_per_output_token": 0.000004,  # Wh/token  
        "power_watts": 180,                   # W during generation
        "latency_factor": 0.3                 # fraction of latency considered compute
    },
    ("gpt-4o", "chat"): {
        "energy_per_input_token": 0.0000021,
        "energy_per_output_token": 0.0000042,
        "power_watts": 185,
        "latency_factor": 0.32
    },
    ("gpt-4o-mini", "standard"): {
        "energy_per_input_token": 0.0000008,
        "energy_per_output_token": 0.0000015,
        "power_watts": 120,
        "latency_factor": 0.25
    },
    ("gpt-4", "standard"): {
        "energy_per_input_token": 0.000003,
        "energy_per_output_token": 0.000006,
        "power_watts": 220,
        "latency_factor": 0.35
    },
    ("gpt-3.5-turbo", "standard"): {
        "energy_per_input_token": 0.000001,
        "energy_per_output_token": 0.000002,
        "power_watts": 140,
        "latency_factor": 0.28
    },
    ("o1", "standard"): {
        "energy_per_input_token": 0.000008,
        "energy_per_output_token": 0.000015,
        "power_watts": 300,
        "latency_factor": 0.45
    },
    ("o1-mini", "standard"): {
        "energy_per_input_token": 0.000004,
        "energy_per_output_token": 0.000007,
        "power_watts": 200,
        "latency_factor": 0.38
    },
    ("unknown", "standard"): {  # Fallback
        "energy_per_input_token": 0.000002,
        "energy_per_output_token": 0.000004,
        "power_watts": 180,
        "latency_factor": 0.3
    }
}

REGION_REGISTRY = {
    "EU": {
        "carbon_g_per_kwh": 275,    # grams CO2 per kWh
        "water_l_per_kwh": 5        # liters per kWh
    },
    "US": {
        "carbon_g_per_kwh": 417,
        "water_l_per_kwh": 7
    },
    "ASIA": {
        "carbon_g_per_kwh": 600,
        "water_l_per_kwh": 10
    },
    "RENEWABLE": {
        "carbon_g_per_kwh": 50,
        "water_l_per_kwh": 1
    }
}

# EXACT prompt_type values from classifyPrompt()
PROMPT_TYPE_MULTIPLIER = {
    "creative-writing": 1.1,
    "explanation": 1.05, 
    "summarization": 0.85,
    "pricing": 1.0,
    "general": 1.0
}

# EXACT domain values from detectDomain()
DOMAIN_MULTIPLIER = {
    "programming": 1.25,
    "marketing": 1.15,
    "finance": 1.20,
    "health": 1.10,
    "general": 1.0
}

# EXACT language values from detectLanguage()
LANGUAGE_MULTIPLIER = {
    "en": 1.0,
    "es": 1.05,
    "fr": 1.05,
    "de": 1.05,
    "it": 1.0
}

# EXACT ui_interaction keys from ChatGPTDetector
UI_MULTIPLIER = {
    "regenerate_used": 2.0,          # Full second inference
    "suggested_prompt_used": 1.05,   # Mild increase  
    "image_attached": 1.35,          # Vision encoder cost
    "file_attached": 1.25,           # File parsing cost
    "voice_input": 1.15,             # STT cost
    "tool_active": 1.30              # Tool invocation overhead
}
