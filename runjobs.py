from interact import *
from sqlalchemy import create_engine #why sqlalchemy? Why not?

db = create_engine('sqlite+pysqlite:///static/db/sms.db')

def main(): #This is a little hacky and also untested. It may be completely useless.
    while True: #just keep going and going and going
        #grab everything in the schedules table
        df = pd.read_sql('SCHEDULES',db)
        #filter it down to just things need to be run
        #technically we will run everything a little but late, but within a couple of seconds so it really doesn't matter...right?
        runs = df[df['NEXT_RUN']<datetime.now()] #I think the df column might need to be strptime'd
        results = runs['QID'].tolist() #get a list of things to run
        #normal result run process
        if len(results)>0: #if there's anything to run, do it
            f = create_csv(results)
            send_email(f,session['email'])
            #set last run and next run times
            with db.begin() as con: #temporarily open a connection
                for r in runs.iterrows():
                    con.execute("update SCHEDULES set LAST_RUN=datetime('now','localtime'),NEXT_RUN=datetime('now','localtime','+%s seconds')" % r['FREQUENCY'].iloc(0)) #This is normally pretty dangerous. But since the frequency column is forced as an integer, it should be safe enough

if __name__=="__main__":
    main()