# the constants are in a different file to keep this one more organized
from energy_calc_constants import *

# should this all be a class too?

# the longer a conversation, the more energy it consumes
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
    # event is the data being sent by the plugin
    # we grab the variables we need out of it for our calculations
    tokens_in = event["prompt"]["tokens_in"]
    tokens_out = event["response"]["tokens_out"]
    latency_ms = event["response"]["latency_ms"]
    streaming_ms = event["response"]["streaming_duration_ms"]

    model_name = event["model"]["model_name"]
    model_mode = event["model"]["model_mode"]

    # we grab the coefficients from the model registry, throw an error if there is no entry
    coeff = MODEL_REGISTRY.get((model_name, model_mode))
    if coeff is None:
        raise ValueError(f"No model coefficients for {model_name} / {model_mode}")

    # Base token energy
    # we use the coefficients with the tokens to calculate energy consumption on tokens
    e_tokens = (
        coeff["energy_per_input_token"] * tokens_in +
        coeff["energy_per_output_token"] * tokens_out
    )

    # Base time energy
    # we calculate energy consumption based on time spent by model on generating response
    t_active_s = (streaming_ms + coeff["latency_factor"] * latency_ms) / 1000
    e_time = coeff["power_watts"] * t_active_s / 3600

    # then add the two values together
    e_base = e_tokens + e_time

    # Prompt metadata multipliers
    
    prompt_type = event["prompt"]["prompt_type"]
    domain = event["prompt"]["domain"]
    language = event["prompt"]["language"]
    conversation_length = event["prompt"]["conversation_length"]
    is_followup = event["prompt"]["is_followup"]

    # we get our multipliers from the various constants, with a base value of 1 
    m_prompt = PROMPT_TYPE_MULTIPLIER.get(prompt_type, 1.0)
    m_domain = DOMAIN_MULTIPLIER.get(domain, 1.0)
    m_language = LANGUAGE_MULTIPLIER.get(language, 1.0)
    m_context = context_multiplier(conversation_length, is_followup)

    # UI interaction multipliers
    # these are boolean fields, so we loop through all of them, increasing the multiplier in case of True
    ui = event["ui_interaction"]
    m_ui = 1.0
    for key, value in ui.items():
        if value: # so only if it's True
            m_ui *= UI_MULTIPLIER.get(key, 1.0)

    # Final energy
    # multiplying the base value with all the multipliers
    return e_base * m_prompt * m_domain * m_language * m_context * m_ui

    # EU as a default region for now, at the moment there is no region detection
    # we could do this with the timezone difference, maybe
def estimate_co2_grams(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")

    carbon_intensity = region_info["carbon_g_per_kwh"]
    energy_kwh = energy_wh / 1000
    # calculate carbon intensity based on the energy consumption
    return energy_kwh * carbon_intensity

def estimate_water_liters(energy_wh, region="EU"):
    region_info = REGION_REGISTRY.get(region)
    if region_info is None:
        raise ValueError(f"No region defaults for {region}")

    water_intensity = region_info["water_l_per_kwh"]
    energy_kwh = energy_wh / 1000
    # calculate water intensity based on energy consumption
    return energy_kwh * water_intensity

    # a single function to return the three values we need
def compute_environmental_impact(event, region="EU"):
    energy_wh = estimate_energy_wh(event)
    co2_g = estimate_co2_grams(energy_wh, region)
    water_l = estimate_water_liters(energy_wh, region)

    return {
        "energy_wh": energy_wh,
        "co2_g": co2_g,
        "water_l": water_l
    }


