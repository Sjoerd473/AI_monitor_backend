CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS models (
  model_id SERIAL PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_mode TEXT NOT NULL,
  UNIQUE(model_name, model_mode)
);

CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  session_start TIMESTAMPTZ NOT NULL,
  session_prompt_count INTEGER NOT NULL,
  session_duration INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS prompts (
  prompt_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  session_id TEXT NOT NULL REFERENCES sessions(session_id),
  model_id INTEGER NOT NULL REFERENCES models(model_id) ON DELETE CASCADE,
  conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id),
  characters_in INTEGER NOT NULL,
  tokens_in INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  domain TEXT NOT NULL,
  type TEXT NOT NULL,
  language TEXT NOT NULL,
  source TEXT NOT NULL,
  energy_consumption_wh FLOAT NOT NULL,
  CO2_output_g FLOAT NOT NULL,
  water_consumption_l FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS responses (
  response_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  character_out INTEGER NOT NULL,
  latency FLOAT NOT NULL,
  streaming_duration FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS environment (
  env_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  browser TEXT NOT NULL,
  version INT NOT NULL,
  os TEXT NOT NULL,
  viewport TEXT NOT NULL,
  timezone INT NOT NULL,
  region TEXT NOT NULL,
  plugin_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ui_interactions (
  interaction_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  regenerate_used BOOL NOT NULL,
  suggested_prompt_used BOOL NOT NULL,
  image_attached BOOL NOT NULL,
  file_attached BOOL NOT NULL,
  voice_input BOOL NOT NULL,
  tool_active BOOL NOT NULL
);

CREATE TABLE IF NOT EXISTS api_tokens (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,   
    token_hash  TEXT NOT NULL UNIQUE, 
    created_at  TIMESTAMPTZ DEFAULT now(),
    last_used   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS download_log (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    downloaded_at TIMESTAMPTZ DEFAULT now()
);