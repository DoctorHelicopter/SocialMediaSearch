All of the files necessary to run this application are included in this archive!
Some prerequisites are shown below - all are available either as open source or with free licensing.

You will need the following:

-Python 2.7.x
--Flask
--pysqlite
--pandas

-VisualCron

-A Gmail account (dedicated to this, ideally)

notes:
use some sort of task scheduler to instantiate interact.py based on schedule. visual cron?
instantiate.py will handle writing results to DB and sending emails

fuck that, that seems stupid and probably wont work. 
don't schedule them. make an active flag, and a job that will run all active queries by trigger - i.e. have a button that will immediately execute all active jobs (or all selected ones?)
also have a last run column, i guess

maybe create a separate schedule table - have the queries isolated, and another table that has schedule details that can be viewed by...something. vcron maybe.

PRIMARY CONCERNS:
-multiple users...I haven't built a message queue into this, but I could. Would require celery most likely, and a message queue. rabbitmq is nice and familiar
-security - do we need it? I guess logon security would be good, to make sure unauthorized users don't flood the system with requests. But there's no sensitive data.
-Should we have the ability to put in a request for a new service? 
-Error handling - do we notify the user, or the dev?

-ALTERNATE METHOD!
-have two separate tables, keywords and sites, and tie each of those to users
-Then have a third table for queries
-Users could have the first two tables exposed along with a scheduler, and manually create queries from that. 
--PROS: Very flexible
--CONS: More work for the users