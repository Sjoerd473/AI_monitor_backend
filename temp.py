from scripts.energy_calc import compute_environmental_impact

boop = {'schema_version': 1, 'timestamp': '2026-03-07T06:07:13.653Z', 'user': {'user_id': '32612bd63857f07f135f5a6656f5352d664054bfedb758e6f6e974db309fecf4'}, 'session': {'session_id': 'e2ad615f6bf73b2c943ca48e8c1ef827', 'session_start': '2026-03-06T17:54:15.834Z', 'session_prompt_count': 28, 'session_duration_ms': 43944077, 'time_since_last_prompt_ms': 42910200}, 'prompt': {'text_length': 7, 'tokens_in': 2, 'prompt_type': 'general', 'domain': 'general', 'language': 'en', 'is_followup': True, 'message_index': 6, 'conversation_length': 12, 'safety_category': 'safe', 'timestamp': '2026-03-07T06:07:13.653Z'}, 'response': {'tokens_out': 36, 'characters_out': 134, 'latency_ms': 33741.80000001192, 'streaming_duration_ms': 33741.69999998808}, 'model': {'model_name': 'unknown', 'model_mode': 'standard'}, 'ui_interaction': {'regenerate_used': False, 'suggested_prompt_used': False, 'image_attached': False, 'file_attached': False, 'voice_input': False, 'tool_active': False}, 'environment': {'hostname': 'chatgpt.com', 'pathname': '/', 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36', 'language': 'en-US', 'screen': '1646x1029'}, 'source': 'chatgpt', 'conversation_id': 'unknown'}


# print(boop)

boopo= compute_environmental_impact(boop)

arr = []

for x,y in boopo.items():
    boop["prompt"].update({x:y})    

print(boop["user"])
print(boop["session"])
print(boop["prompt"])
print(boop["model"])
print(boop["ui_interaction"])
print(boop['response'])
print(boop['source'])
print(boop['environment'])

for obj in arr:
    querty1 = func1(obj[...])
    query2 = func2(obj[...])

    def get_query(self, arr):
        query= ''
        if arr["user"]:
            query = "INSERT INTO users (user_id) VALUES (%s)"
        elif arr["session"]:
            query = "INSERT INTO sessions (session_start, session_prompt_count, session_duration) VALUES (%s, %s, %s)"
        return query
        
    def get_params(self, arr, type):
        # these need to be finetuned a lot, not all tables need to be completely updated every time
       match type:
           case "users":
               return [arr["user"]["user_id"]]
           case "models":
               ...
           case "sessions":
               return [arr["session"]["session_id"], arr["session"]["session_prompt_count"]["session_duration_ms"]]
           case "prompts":
                return [
                    arr["user"]["user_id"],
                    arr["session"]["session_id"],
                    arr["model_id"], #THIS DOES NOT EXIST YET!!
                    arr["prompt"]["character_in"],
                    arr["prompt"]["tokens_in"],
                    arr["prompt"]["timestamp"],
                    arr["prompt"]["domain"],
                    arr["prompt"]["prompt_type"],
                    arr["prompt"]["safety_category"],
                    arr["prompt"]["language"],
                    arr["source"],
                    arr["prompt"]["energy_wh"],
                    arr["prompt"]["co2_g"],
                    arr["prompt"]["water_l"]]
           case "response":
                return [
                    # PROMPTID
                    arr["response"]["characters_out"],
                    arr["response"]["latency_ms"],
                    arr["response"]["streaming_duration_ms"]
                ]
           case "env":
                # NOT RETURNING THE RIGHT VALUES AT THE MOMENT
                return [
                    # PROMPTID
                    arr["env"][""]
                ]
           case "ui":
                return [
                    # PROMPTID
                ]
           
        def insert_prompts(self, batch):

        # pseudo-representation
# models_map = { (model_name, model_mode): model_id for model_id, model_name, model_mode in db.get_models() }
        users_rows = []
        models_rows = []
        sessions_rows = []
        prompts_rows =[]
        responses_rows = []
        environment_rows = []
        ui_interactions_rows = []

        for data_object in batch:
            users_rows.append(self.get_params(data_object, 'users'))
            models_rows.append(self.get_params(data_object, 'models'))
            sessions_rows.append(self.get_params(data_object, 'sessions'))
            prompts_rows.append(self.get_params(data_object, 'prompts'))
            responses_rows.append(self.get_params(data_object, 'response'))
            environment_rows.append(self.get_params(data_object, 'env'))
            ui_interactions_rows.append(self.get_params(data_object, 'ui'))
        
        seq_of_params_users = [tuple(row) for row in users_rows]
        seq_of_params_models = [tuple(row) for row in models_rows]
        seq_of_params_sessions = [tuple(row) for row in sessions_rows]
        seq_of_params_prompts = [tuple(row) for row in prompts_rows]
        seq_of_params_responses = [tuple(row) for row in responses_rows]
        seq_of_params_env = [tuple(row) for row in environment_rows]
        seq_of_params_ui = [tuple(row) for row in ui_interactions_rows]
            
        self._write_many(self.INSERT_QUERIES["users"], seq_of_params_users)
        self._write_many(self.INSERT_QUERIES["models"], seq_of_params_models)
        self._write_many(self.INSERT_QUERIES["sessions"], seq_of_params_sessions)
        self._write_many(self.INSERT_QUERIES["prompts"], seq_of_params_prompts)
        self._write_many(self.INSERT_QUERIES["response"], seq_of_params_responses)
        self._write_many(self.INSERT_QUERIES["env"], seq_of_params_env)
        self._write_many(self.INSERT_QUERIES["ui"], seq_of_params_ui)
    
def insert_prompts(self, batch):
    """Insert a batch of prompts and all related tables (users, sessions, responses, environment, UI)."""

    # --- Step 0: Prepare model lookup ---
    existing_models = {
        (m["model_name"], m["model_mode"]): m["model_id"]
        for m in self.get_models()
    }

    # Identify new models not yet in DB
    new_models = set()
    for b in batch:
        model = b["model"]
        key = (model["model_name"], model["model_mode"])
        if key not in existing_models:
            new_models.add(key)

    # Insert missing models
    if new_models:
        self._write_many(self.INSERT_QUERIES["models"], [tuple(m) for m in new_models])
        # Re-fetch models to update mapping
        existing_models.update({
            (m["model_name"], m["model_mode"]): m["model_id"]
            for m in self.get_models()
        })

    # --- Step 1: Build parent rows ---
    users_rows = [(b["user"]["user_id"],) for b in batch]
    sessions_rows = [
        (
            b["session"]["session_id"],
            b["session"]["session_start"],
            b["session"]["session_prompt_count"],
            b["session"]["session_duration_ms"]
        )
        for b in batch
    ]

    # Insert parent tables
    self._write_many(self.INSERT_QUERIES["users"], users_rows)
    self._write_many(self.INSERT_QUERIES["sessions"], sessions_rows)

    # --- Step 2: Build prompts ---
    prompts_rows = []
    for b in batch:
        user = b["user"]
        session = b["session"]
        model = b["model"]
        prompt = b["prompt"]

        model_id = existing_models[(model["model_name"], model["model_mode"])]

        prompts_rows.append((
            user["user_id"],
            session["session_id"],
            model_id,
            prompt["text_length"],
            prompt["tokens_in"],
            prompt["timestamp"],
            prompt["domain"],
            prompt["prompt_type"],
            prompt["safety_category"],
            prompt["language"],
            b["source"],
            prompt["energy_wh"],
            prompt["co2_g"],
            prompt["water_l"]
        ))

    # Bulk insert prompts and get their IDs
    prompt_ids = self._write_many_returning(self.INSERT_QUERIES["prompts"], prompts_rows)

    # --- Step 3: Build child rows ---
    responses_rows = []
    env_rows = []
    ui_rows = []

    for i, b in enumerate(batch):
        pid = prompt_ids[i]
        response = b["response"]
        env = b["environment"]
        ui = b["ui_interaction"]

        responses_rows.append((
            pid,
            response["characters_out"],
            response["latency_ms"],
            response["streaming_duration_ms"]
        ))

        env_rows.append((
            pid,
            env["browser"],
            env["version"],
            env["os"],
            env["viewport"],
            env["timezone"],
            env["plugin_version"]
        ))

        ui_rows.append((
            pid,
            ui["regenerate_used"],
            ui["suggested_prompt_used"],
            ui["image_attached"],
            ui["file_attached"],
            ui["voice_input"],
            ui["tool_active"]
        ))

    # --- Step 4: Bulk insert child tables ---
    self._write_many(self.INSERT_QUERIES["responses"], responses_rows)
    self._write_many(self.INSERT_QUERIES["environment"], env_rows)
    self._write_many(self.INSERT_QUERIES["ui"], ui_rows)