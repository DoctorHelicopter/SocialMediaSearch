__author__ = "Sam Rubin"
__created__ = "1/4/2016"
from flask import Flask, render_template, url_for, request, redirect, config, g, session
import sqlite3 as sq3
import pandas as pd
from uuid import uuid4
from interact import *

DATABASE = 'static/db/sms.db' #local sqlite file. This was done for portability, if it's hosted on a dedicated server all of the sqlite stuff should be translated to something more robust.
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'f\xcb2FW\x90\xded\x9a\x05\x86\x0e\xd7&uR\xb6n\xf8TY\x1b\xb3\t' #This should probably be encoded in a text file and decoded here for slightly more security. Deal with that later.

@app.route('/')
def index():
    #Start here
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.form['username'] not in [None,'']:
        #This is my really lazy security - if fleshed out I'll add some real stuff here
        session['username'] = request.form['username']
        users = g.db.execute("select UID, USERNAME, EMAIL from USERS where USERNAME=?", (session['username'],)).fetchall()
        if len(users)>0: #user exists, update logon time and keep going
            session['uid'] = users[0][0] #Grab the first UID that shows up. I'm assuming usernames are unique. I need to check for that later, but theoretically this should keep them unique anyway.
            session['email'] = users[0][2]
            print "Users exists: ", session['uid']
            g.db.execute("update USERS set LAST_LOGON=datetime('now','localtime') WHERE USERNAME=?", (session['username'],))
            g.db.commit()
        else: #create a new user automatically...because it's easy
            #should probably prompt for more info here...but I don't use the other columns yet so it's backburner
            print "Creating new user"
            g.db.execute("insert into USERS (UID, USERNAME, EMAIL, LAST_LOGON) values (?, ?, ?, datetime('now','localtime'))",(str(uuid4()),session['username'], request.form['email']))
            g.db.commit()
        return redirect(url_for('menu'))
    #If you tried to go to this page without giving a username, redirect to login - username is required
    return redirect(url_for('login'))

@app.route('/menu', methods=['POST','GET'])
def menu():
    #This is really just here so the URL changes - more important if there's a security model, there would be logon checks
    return render_template('menu.html', username=session['username'])

@app.route('/menu/choice', methods=['POST'])
def menu_choice():
    #simple switch based on the button from the previous page. I guess they could have been two separate forms or methods but this is easy enough.
    if request.form['choice'] == 'Create New Query':
        return redirect(url_for('newquery'))
    elif request.form['choice'] == 'View Existing Queries':
        return redirect(url_for('queries'))
    elif request.form['choice'] == 'View Scheduled Query Results':
        return redirect(url_for('schedules'))
    #If somehow your choice wasn't on the list (you made a custom request for some reason...) then show what you managed to enter on a test page I made instead of passing through
    #If someone sees this, they're trying to break the site. Or they are just not good with computer.
    return render_template('test.html', text='You entered: %s. How/why?' % request.form['choice'])

@app.route('/newquery', methods=['POST','GET'])
def newquery():
    qlist = []
    if request.method == 'GET':
        #If you did a GET from the menu, just show the form
        #technically...it was a post. But there was no data, so it ends up coming through as a get. Is this a hacky workaround? Yes. Does it matter if it works? Maybe.
        return render_template('newquery.html')
    elif request.method == 'POST':
        #If it was posted with content, make sure it worked, then give success message
        #do logic, then return to the page with success message
        sql = "insert into QUERIES (QID, UID, SITE, KEYWORD, CREATED) VALUES (?, ?, ?, ?, datetime('now','localtime'))" 
        statements = []
        for s in request.form.getlist('site'): #Check through all of the selected sites
            print s
            for kw in request.form['keywords'].split(','): #iterate through our KWs
                #gather them in a list first. That way, if there's a problem with any of them, the whole thing will abort instead of writing partial records
                statements.append({'site'       : str(s),
                                   'keyword'    : str(kw).strip()
                    })
        #Now we have a list of statements that we know will work. 
        for st in statements:
            qid = str(uuid4())
            qlist.append(qid)
            g.db.execute(sql, (qid, session['uid'], st['site'], st['keyword']))
            g.db.commit()

        runs = request.form.getlist('runnow')
        if len(runs)>0 and runs[0] == 'yes':
            #run the most recently added queries and send an email
            print "Running now"
            results = run_search(qlist)
            f = create_csv(results)
            send_email(f,[session['email']])
            message = 'Sucessfully created and ran query'
        elif len(statements)>0:
            message = 'Successfully created a new query'
        else:
            message = ''
        return render_template('newquery.html', msg=message)

@app.route('/queries', methods=['POST','GET'])
def queries():
    if request.method == 'GET':
        #show all existing queries for the current user
        pass #don't need to do anything else
    elif request.method == 'POST': #Do logic here
        todo = request.form['todo']
        selected = request.form.getlist('selected')
        #ability to delete selected
        if len(selected)==0:
            qlist = g.db.execute("select * from QUERIES join USERS on USERS.UID=QUERIES.UID where QUERIES.UID=?",(session['uid'],)).fetchall()
            print qlist
            return render_template('queries.html',qlist=qlist,message="You didn't select anything!")
        elif todo == 'Delete selected':
            for s in selected: #should I have a pop-up confirmation? Maybe. That's a javascript thing
                g.db.execute("delete from QUERIES where QID=?",(s,))
            g.db.commit()
        #ability to select multiple and run immediately
        elif todo == 'Run selected immediately':
            #Use functions in interact.py to run searches based on selections
            results = request.form.getlist('selected')
            f = create_csv(results)
            send_email(f,session['email'])
        #ability to create a schedule for the selected queries
        elif todo == 'Create schedule for selected':
            session['selected'] = selected #save what was selected so the scheduler can use the list
            return redirect(url_for('newschedule'))
    qlist = g.db.execute("select * from QUERIES join USERS on USERS.UID=QUERIES.UID where QUERIES.UID=?",(session['uid'],)).fetchall()
    print qlist
    return render_template('queries.html',qlist=qlist)

@app.route('/schedules', methods=['GET'])
def schedules():
    #show all existing schedules for the current user
    schedules = g.db.execute("select * from SCHEDULES join USERS on SCHEDULES.UID=USERS.UID join QUERIES on QUERIES.QID=SCHEDULES.QID where SCHEDULES.UID=?", (session['uid'],)).fetchall()
    #ability to select a schedule and list results from all time, split by runtime
    print schedules
    return render_template('schedules.html', schedules=schedules)
    
@app.route('/newschedule', methods=['POST','GET'])
def newschedule():
    #some sort of UI to select a freqency to run
    #add chosen schedule connected to selected QIDs to the database table
    #return to the schedule list
    if request.method == 'GET':
        return render_template('newschedule.html')
    elif request.method == 'POST':
        #do logic
        tstart = request.form['tstart']
        tend = request.form['tend']
        freq = request.form['freq']
        queries = session['selected']
        for q in queries:
            g.db.execute("insert into SCHEDULES (SID, QID, UID, CREATED, LAST_RUN, NEXT_RUN, TIME_START, TIME_END, FREQUENCY) values (?,?,?,datetime('now','localtime'),datetime('now','localtime'),datetime('now','localtime','+%s seconds'),?,?,?)"%freq,(str(uuid4()),q,session['uid'],tstart,tend,freq))
        g.db.commit()
        return redirect(url_for('schedules'))
    
@app.route('/results', methods=['POST','GET'])
def results():
    results = []
    todo = request.form['todo']
    #show results for the selected schedule for a given time periods
    selected = request.form.getlist('selected') 
    if todo == 'Delete selected':
        for s in selected: #should I have a pop-up confirmation? Maybe. That's a javascript thing
            g.db.execute("delete from SCHEDULES where SID=?",(s,))
        g.db.commit()
        return redirect(url_for('schedules'))
    elif todo == 'View results for selected':
        for s in selected:
            results.append(g.db.execute("select * from RESULTS where SID=?", (s,)).fetchall())
    #ability to export to csv
    ##then either download immediately or email to someone
    return render_template('results.html',results=results)
    
@app.route('/export', methods=['POST'])
def export():
    #This is the function that will call the exporter and then redirect to the results page
    results = request.form.getlist('selected')
    dest = [d.strip() for d in request.form['dest'].split(',')]
    f = create_csv(results)
    send_email(f,dest)
    return redirect(url_for('results'))

def connect_db():
    return sq3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    #only create DB connection during request periods, that way it's not just sitting there open the entire life of the server
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    #get rid of the connection if there's an issue 
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=app.config['DEBUG'])