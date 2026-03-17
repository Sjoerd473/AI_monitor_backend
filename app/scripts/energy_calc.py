from scripts.energy_calc_constants import *

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

    # ✅ Fallback chain instead of raising
    coeff = (
        MODEL_REGISTRY.get((model_name, model_mode)) or
        MODEL_REGISTRY.get((model_name, "standard")) or
        MODEL_REGISTRY.get(("default", "standard"))
    )
    if coeff is None:
        raise ValueError(f"No model coefficients for {model_name} / {model_mode} and no default found")

    e_tokens = (
        coeff["energy_per_input_token"] * tokens_in +
        coeff["energy_per_output_token"] * tokens_out
    )

    t_active_s = (streaming_ms + coeff["latency_factor"] * latency_ms) / 1000
    e_time = coeff["power_watts"] * t_active_s / 3600
    e_base = e_tokens + e_time

    prompt_type = event["prompt"]["prompt_type"]
    domain = event["prompt"]["domain"]
    language = event["prompt"]["language"]
    conversation_length = event["prompt"]["conversation_length"]
    is_followup = event["prompt"]["is_followup"]

    m_prompt = PROMPT_TYPE_MULTIPLIER.get(prompt_type, 1.0)
    m_domain = DOMAIN_MULTIPLIER.get(domain, 1.0)
    m_language = LANGUAGE_MULTIPLIER.get(language, 1.0)
    m_context = context_multiplier(conversation_length, is_followup)

    ui = event["ui_interaction"]
    m_ui = 1.0
    for key, value in ui.items():
        if value:
            m_ui *= UI_MULTIPLIER.get(key, 1.0)

    return e_base * m_prompt * m_domain * m_language * m_context * m_ui

def estimate_co2_grams(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")
    return (energy_wh / 1000) * region_info["carbon_g_per_kwh"]

def estimate_water_liters(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")
    return (energy_wh / 1000) * region_info["water_l_per_kwh"]

def compute_environmental_impact(event, region="EU"):
    # ✅ Never crash the request — always return something
    try:
        energy_wh = estimate_energy_wh(event)
        co2_g = estimate_co2_grams(energy_wh, region)
        water_l = estimate_water_liters(energy_wh, region)
        return {"energy_wh": energy_wh, "co2_g": co2_g, "water_l": water_l}
    except Exception as e:
        model = event.get("model", {})
        print(f"[EnergyCalc] WARNING: falling back to zeros for {model.get('model_name')}/{model.get('model_mode')}: {e}")
        return {"energy_wh": 0, "co2_g": 0, "water_l": 0}