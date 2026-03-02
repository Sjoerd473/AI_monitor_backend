MODEL_REGISTRY = {
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

def context_multiplier(conversation_length, is_followup):
    m = 1.0
    if conversation_length > 5:
        m += 0.05
    if conversation_length > 10:
        m += 0.10
    if is_followup:
        m += 0.05
    return m

def estimate_energy_wh(event):
    tokens_in = event["prompt"]["tokens_in"]
    tokens_out = event["response"]["tokens_out"]
    latency_ms = event["response"]["latency_ms"]
    streaming_ms = event["response"]["streaming_duration_ms"]

    model_name = event["model"]["model_name"]
    model_mode = event["model"]["model_mode"]

    coeff = MODEL_REGISTRY.get((model_name, model_mode))
    if coeff is None:
        raise ValueError(f"No model coefficients for {model_name} / {model_mode}")

    # Base token energy
    e_tokens = (
        coeff["energy_per_input_token"] * tokens_in +
        coeff["energy_per_output_token"] * tokens_out
    )

    # Base time energy
    t_active_s = (streaming_ms + coeff["latency_factor"] * latency_ms) / 1000
    e_time = coeff["power_watts"] * t_active_s / 3600

    e_base = e_tokens + e_time

    # Prompt metadata multipliers
    prompt_type = event["prompt"]["prompt_type"]
    domain = event["prompt"]["domain"]
    language = event["prompt"]["language"]
    conversation_length = event["prompt"]["conversation_length"]
    is_followup = event["prompt"]["is_followup"]

    m_prompt = PROMPT_TYPE_MULTIPLIER.get(prompt_type, 1.0)
    m_domain = DOMAIN_MULTIPLIER.get(domain, 1.0)
    m_language = LANGUAGE_MULTIPLIER.get(language, 1.0)
    m_context = context_multiplier(conversation_length, is_followup)

    # UI interaction multipliers
    ui = event["ui_interaction"]
    m_ui = 1.0
    for key, value in ui.items():
        if value:
            m_ui *= UI_MULTIPLIER.get(key, 1.0)

    # Final energy
    return e_base * m_prompt * m_domain * m_language * m_context * m_ui

def estimate_co2_grams(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")

    carbon_intensity = region_info["carbon_g_per_kwh"]
    energy_kwh = energy_wh / 1000

    return energy_kwh * carbon_intensity

def estimate_water_liters(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")

    water_intensity = region_info["water_l_per_kwh"]
    energy_kwh = energy_wh / 1000

    return energy_kwh * water_intensity

def compute_environmental_impact(event, region="EU"):
    energy_wh = estimate_energy_wh(event)
    co2_g = estimate_co2_grams(energy_wh, region)
    water_l = estimate_water_liters(energy_wh, region)

    return {
        "energy_wh": energy_wh,
        "co2_g": co2_g,
        "water_l": water_l
    }


