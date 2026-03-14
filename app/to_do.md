To Do:


-- extension/content.js + backend/energy_calc --

- the various text analysis functions of the plugin all need to be written with Regex
- and then be expanded upon much more
- make sure the constants in energy_calc_constants.py still match

- handle viewport insertion better, needs to be mobile/tablet/desktop depending on size

- handle region detection based on timezone offset, drop renewable from constants?

- move energy calculations to the extension perhaps?
- might be useful for the future, to show user data to the user without DB queries

---------------------

-- DB --

- add user_id to sessions table DONE
- add uniqueness constraint to session_id + user_id in sessions DONE

- decide whether to use the conversation_id or a session_id to monitor sessions > conv_id might work more consistently

- configure the pool DONE
- add a .env file DONE

- Write reading prompts DONE

- clear up columns of consumption data > add mw, g etc. DONE


----------------------

-- db_caching.py --

- add all the functions that call the data we need for graphs DONE
- write all the data to a single .json file (with different objects for each graph) DONE
- put it on a cronjob, or some other way to call the file each hour (or so)

- Add a readme.md along with the whole dataset.json to explain relations between tables. Include the DB schema. Or, write down the PKs and FKs


----------------------

-- main.py --

- add an endpoint that returns the .json file with the graph data NO NEED

- add an endpoint that serves the graphs html page

----------------------

-- dashboard.js --

- this will need to be imported in the html file (as a module)

- needs to fetch the data from the endpoint on 'DOMContentLoaded'
- and then immediately run a function to create the charts

- Write graph scripting

- figure out how to bundle this NOT NEEDED

----------------------

-- charts.html --

- design the layout
- write the content


----------------------

-- VPS --

- Clean up the VPS
- Set up the VPS

----------------------

-- Cache --

- Use redis for caching, the current setup will break in prod DONE

----------------------

-- Plugin --

- support other AI sites Gemini, claude? perplexity


----------------------

-- Misc ---

- Write README for both parts
- get plugin onto google play store
- Minimize plugin
- Write a github action to automatically update code on the server DONE

- containerize the plugin DONE

-----------------------


Things just for me to remember

Use connection pooling, maybe add pgBouncer as a middleman
Make everything async done
Do micro batching done
Keep ingestion writes cheap? done
Avoid heavy indexing on ingestion table ??
Use background workers to manage the DB?? done-ish

uvicorn main:app --workers 4

Each worker is like a seperate instance of the application, each with its own memory, so an in-memory buffer will not work


so I would have to write a seperate python file that executes these queries and writes the output to a json file in the backend folder, attach a cronjob to this python file, then instruct the endpoints to read their data from the json file?

0 * * * * /usr/bin/python3 /home/sjoerd/yourproject/precompute_cache.py hourly run for file

- Remeber to write the correct dotenv file on the server