-- USERS
INSERT INTO users (user_id) VALUES
  ('user_001'),
  ('user_002');

-- MODELS
INSERT INTO models (model_name, model_mode) VALUES
  ('gpt-4o', 'chat'),
  ('gpt-4o-mini', 'chat'),
  ('claude-3-opus', 'chat');

-- SESSIONS
INSERT INTO sessions (session_id, session_start, session_prompt_count, session_duration) VALUES
  ('sess_001', '2026-03-05 10:15:00', 3, 420),
  ('sess_002', '2026-03-05 11:00:00', 1, 180);

-- PROMPTS
INSERT INTO prompts (
  user_id, session_id, model_id,
  character_in, tokens_in, domain, type, safety_cat,
  language, source, energy_consumption, CO2_output, water_consumption
) VALUES
  ('user_001', 'sess_001', 1,
   120, 30, 'general', 'prompt', 'safe',
   'en', 'extension', 0.0021, 0.0009, 0.15),

  ('user_001', 'sess_001', 2,
   340, 80, 'coding', 'prompt', 'safe',
   'en', 'extension', 0.0035, 0.0014, 0.22),

  ('user_002', 'sess_002', 3,
   200, 50, 'research', 'prompt', 'safe',
   'en', 'extension', 0.0042, 0.0018, 0.30);

-- RESPONSES
INSERT INTO responses (prompt_id, character_out, latency, streaming_duration) VALUES
  (1, 450, 0.85, 1.20),
  (2, 1200, 1.10, 2.50),
  (3, 800, 0.95, 1.80);

-- ENVIRONMENT
INSERT INTO environment (
  prompt_id, browser, version, os, viewport, timezone, plugin_version
) VALUES
  (1, 'Chrome', 122, 'Windows 11', '1920x1080', 1, '1.0.0'),
  (2, 'Chrome', 122, 'Windows 11', '1920x1080', 1, '1.0.0'),
  (3, 'Chrome', 122, 'macOS 14', '1440x900', 1, '1.0.0');

-- UI INTERACTIONS
INSERT INTO ui_interactions (
  prompt_id, regenerate_used, suggested_prompt_used,
  image_attached, file_attached, voice_input, tool_active
) VALUES
  (1, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE),
  (2, TRUE, FALSE, TRUE, FALSE, FALSE, TRUE),
  (3, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE);