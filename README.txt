All of the files necessary to run this application are included in this archive!
Some prerequisites are shown below - all are available either as open source or with free licensing.

ASSUMPTONS:
You have the following:

-Python 2.7.x (developed in 2.7.11)
--flask
--pysqlite
--pandas
--praw (reddit API)

-Cron (or any other task scheduler; for running scheduled tasks)
(Note: This isn't actually implemented yet. But the idea would be to constantly run a script (runjobs.py) that checks for schedules to run)

-A dedicated mail account to send from (Gmail by default, configurable to any SMTP server)

PRIMARY CONCERNS:
-multiple users...I haven't built a message queue into this, but I could. Would require celery most likely, and a message queue. rabbitmq is nice and familiar
-security - do we need it? I guess logon security would be good, to make sure unauthorized users don't flood the system with requests, or randomly delete stuff.
-Should we have the ability to put in a request for a new website to search? 
-Error handling - do we notify the user, or the dev?

ALTERNATE METHOD!
-have two separate tables, keywords and sites, and tie each of those to users
-Then have a third table for queries
-Users could have the first two tables exposed along with a scheduler, and manually create queries from that. 
--PROS: Very flexible
--CONS: More work for the users