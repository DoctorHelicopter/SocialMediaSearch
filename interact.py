def run_search(qlist):
    #take in a list of queries and dispatch other functions
    for q in qlist:
        query = g.db.execute("select * from QUERIES where QID=?",(q,)).fetchall()[0]
        if q[2] == 'reddit':
            get_reddit(q)
        elif q[2] == 'facebook':
            get_facebook(q)
        elif q[2] == 'twitter':
            get_twitter(q)
        elif q[2] == 'instagram':
            get_instagram(q)

def get_reddit(q):
    results = []
    kw = q[3]
    #need to define start and end time range as part of the query
    tstart = q[4]
    tend = q[5]
    #run a search for all matching posts
    #for each match, write it to the result database

def get_facebook(q):
    results = []

def get_twitter(q):
    results = []

def get_instagram(q):
    results = []

def create_csv(results):
    #take a list of result IDs
    df = pd.read_sql_query("select * from RESULTS where RID in (?)",(', '.join(["'"+r+"'" for r in results])),g.db)
    #create the csv
    #save it to static/media
    filename = '/static/media/result_%s.csv' % datetime.now().strftime('%Y%m%d%H%M%S')
    df.to_csv(filename,index=False)
    #return the filepath
    return filename

def send_email(f,dest): #default to send to current user unless otherwise specified
    #take a filepath
    #connect to a gmail account for now...this could really be anything, I could modify this to work with EWS too
    msg = 'Attached is the file generated at %s for your query.' % datetime.strptime(f.split('_')[1].split('.')[0],'%Y%m%d%H%M%S').strftime('%m/%d/%Y %H:%M:%S') #This is such an ugly method but I suppose it works.
    msg = ' Please submit a support ticket if you experience any issues.'
    #send the file to the current logged in user's email
    pass
