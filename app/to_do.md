To Do:


-- extension/content.js + backend/energy_calc --

- handle models not in the energy_calc variables


---> make sure the constants in energy_calc_constants.py still match

---> handle region detection based on timezone offset, drop renewable from constants?



---------------------

-- DB --

- Write a simple script to insert some models into the model table




- grab conv_id from the url individually for each ai, and save it in prompt data?
- or in it's own table




----------------------

-- db_caching.py --



- Add a readme.md along with the whole dataset.json to explain relations between tables. Include the DB schema. Or, write down the PKs and FKs


----------------------

-- main.py --

- add rate limiting to limit the amount of sends from a client

----------------------

-- dashboard.js --

- this will need to be imported in the html file (as a module)

- needs to fetch the data from the endpoint on 'DOMContentLoaded'
- and then immediately run a function to create the charts

- Write graph scripting


----------------------

-- charts.html --

- design the layout
- make the charts look nice
- they need the right labels
- write the content


----------------------

-- VPS --



----------------------

-- Cache --



----------------------

-- Plugin --

- Write the HTML for the plugin


----------------------

-- Misc ---

- Write README for both parts
- Write README for data
- get plugin onto google play store






-----------------------


Things just for me to remember

Use connection pooling, maybe add pgBouncer as a middleman


uvicorn main:app --workers 4

Each worker is like a seperate instance of the application, each with its own memory, so an in-memory buffer will not work


so I would have to write a seperate python file that executes these queries and writes the output to a json file in the backend folder, attach a cronjob to this python file, then instruct the endpoints to read their data from the json file?

0 * * * * /usr/bin/python3 /home/sjoerd/yourproject/precompute_cache.py hourly run for file

- Remeber to write the correct dotenv file on the server DONE