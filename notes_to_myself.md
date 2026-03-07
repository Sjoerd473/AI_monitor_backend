Use connection pooling, maybe add pgBouncer as a middleman
Make everything async
Do micro batching
Keep ingestion writes cheap?
Avoid heavy indexing on ingestion table
Use background workers to manage the DB??


so I would have to write a seperate python file that executes these queries and writes the output to a json file in the backend folder, attach a cronjob to this python file, then instruct the endpoints to read their data from the json file?

0 * * * * /usr/bin/python3 /home/sjoerd/yourproject/precompute_cache.py hourly run for file

To Do:

-Write documentation for plugin
-Write README for both parts
-Write insertion prompt
-Write reading prompts
-Write graph scripting

-Clean up the server
-Set up the server

-Minimize plugin, figure out how to serve it to users
-Write a github action to automatically update code on the server

array with objects arrives
we loop over the array
each object needs to be split up into objects, because each of them has its own query
