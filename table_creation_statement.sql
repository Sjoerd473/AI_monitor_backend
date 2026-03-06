CREATE TABLE users (
  user_id TEXT PRIMARY KEY
);

CREATE TABLE models (
  model_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_mode TEXT NOT NULL
);

CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  session_start TIMESTAMP NOT NULL,
  session_prompt_count INTEGER NOT NULL,
  session_duration INTEGER NOT NULL
);

CREATE TABLE prompts (
  prompt_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  session_id TEXT NOT NULL REFERENCES sessions(session_id),
  model_id INTEGER NOT NULL REFERENCES models(model_id),
  character_in INTEGER NOT NULL,
  tokens_in INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL
  domain TEXT NOT NULL,
  type TEXT NOT NULL,
  safety_cat TEXT,
  language TEXT NOT NULL,
  source TEXT NOT NULL,
  energy_consumption FLOAT NOT NULL,
  CO2_output FLOAT NOT NULL,
  water_consumption FLOAT NOT NULL
);

CREATE TABLE responses (
  response_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id),
  character_out INTEGER NOT NULL,
  latency FLOAT NOT NULL,
  streaming_duration FLOAT NOT NULL
);

CREATE TABLE environment (
  env_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id),
  browser TEXT NOT NULL,
  version INT NOT NULL,
  os TEXT NOT NULL,
  viewport TEXT NOT NULL,
  timezone INT NOT NULL,
  plugin_version TEXT NOT NULL
);

CREATE TABLE ui_interactions (
  interaction_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prompt_id INTEGER UNIQUE NOT NULL REFERENCES prompts(prompt_id),
  regenerate_used BOOL NOT NULL,
  suggested_prompt_used BOOL NOT NULL,
  image_attached BOOL NOT NULL,
  file_attached BOOL NOT NULL,
  voice_input BOOL NOT NULL,
  tool_active BOOL NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_prompts_session_id ON prompts(session_id);
CREATE INDEX idx_prompts_model_id ON prompts(model_id);
CREATE INDEX idx_responses_prompt_id ON responses(prompt_id);
CREATE INDEX idx_environment_prompt_id ON environment(prompt_id);
CREATE INDEX idx_ui_prompt_id ON ui_interactions(prompt_id);