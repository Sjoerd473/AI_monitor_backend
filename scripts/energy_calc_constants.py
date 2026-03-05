# these are the various values and multipliers that are used in the calculations
# for energy, water and CO2
# they are more like estimates than extremely researched values

MODEL_REGISTRY = {
    # a tuple as a key-value pair, as a model can have different modes = different coefficients
    ("gpt-4o", "text"): {
        "energy_per_input_token": 0.000002,   # Wh/token
        "energy_per_output_token": 0.000004,  # Wh/token
        "power_watts": 180,                   # W during generation
        "latency_factor": 0.3                 # fraction of latency considered compute
    },
    ("gpt-4-turbo", "text"): {
        "energy_per_input_token": 0.000003,
        "energy_per_output_token": 0.000006,
        "power_watts": 220,
        "latency_factor": 0.35
    },
    ("claude-3-opus", "text"): {
        "energy_per_input_token": 0.000005,
        "energy_per_output_token": 0.000009,
        "power_watts": 260,
        "latency_factor": 0.4
    },
    ("gemini-1.5-pro", "text"): {
        "energy_per_input_token": 0.000003,
        "energy_per_output_token": 0.000006,
        "power_watts": 200,
        "latency_factor": 0.3
    }
}

REGION_REGISTRY = {
    "EU": {
        "carbon_g_per_kwh": 275,   # grams CO2 per kWh
        "water_l_per_kwh": 5       # liters per kWh
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

PROMPT_TYPE_MULTIPLIER = {
    "question": 1.0,
    "rewrite": 0.9,
    "summarize": 0.8,
    "creative": 1.1,
    "code": 1.2,
    "analysis": 1.15
}

DOMAIN_MULTIPLIER = {
    "general": 1.0,
    "coding": 1.25,
    "math": 1.2,
    "legal": 1.15,
    "medical": 1.15,
    "creative": 1.05
}

LANGUAGE_MULTIPLIER = {
    "en": 1.0,
    "zh": 1.1,   
    "ja": 1.15,
    "ko": 1.1,
    "ar": 1.05,
    "de": 1.05,
    "fr": 1.05,
    "it": 1.0
}

UI_MULTIPLIER = {
    "regenerate_used": 2.0,        # full second inference
    "suggested_prompt_used": 1.05, # mild increase
    "image_attached": 1.35,        # vision encoder cost
    "file_attached": 1.25,         # file parsing cost
    "voice_input": 1.15,           # STT cost
    "tool_active": 1.30            # tool invocation overhead
}