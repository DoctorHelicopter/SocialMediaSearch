__author__ = "Sam Rubin"
__created__ = "1/4/2016"
from flask import Flask, render_template, url_for, request, redirect, config, g, session
import sqlite3 as sq3
import pandas as pd
from uuid import uuid4
from interact import *

DATABASE = 'static/db/sms.db' #local sqlite file
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
        users = g.db.execute("select UID, USERNAME from USERS where USERNAME=?", (session['username'],)).fetchall()
        if len(users)>0: #user exists, update logon time and keep going
            session['uid'] = users[0][0] #Grab the first UID that shows up. I'm assuming usernames are unique. I need to check for that later, but theoretically this should keep them unique anyway.
            print "Users exists: ", session['uid']
            g.db.execute("update USERS set LAST_LOGON=datetime('now','localtime') WHERE USERNAME=?", (session['username'],))
            g.db.commit()
        else: #create a new user automatically...because lazy
            #should probably prompt for more info here...but I don't use the other columns yet so it's backburner
            print "Creating new user"
            g.db.execute("insert into USERS (UID, USERNAME, LAST_LOGON) values (?, ?, datetime('now','localtime'))",(str(uuid4()),session['username']))
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
    elif request.form['choice'] == 'Create New Scheduled Query':
        return redirect(url_for('newschedule'))
    elif request.form['choice'] == 'View Scheduled Query Results':
        return redirect(url_for('schedules'))
    #If somehow your choice wasn't on the list (you made a custom request for some reason...) then show what you managed to enter on a test page I made instead of passing through
    #If someone sees this, they're trying to break the site. Or they are just not good with computer.
    return render_template('test.html', text='You entered: %s. How/why?' % request.form['choice'])

@app.route('/newquery', methods=['POST','GET'])
def newquery():
    if request.method == 'GET':
        #If you did a GET from the menu, just show the form
        #technically...it was a post. But there was no data, so it ends up coming through as a get. Is this a hacky workaround? Yes. Does it matter if it works? Maybe.
        return render_template('new_query.html')
    elif request.method == 'POST':
        #If it was posted with content, make sure it worked, then give success message
        #do logic, then return to the page with success message
        sql = "insert into QUERIES (QID, UID, SITE, KEYWORD, FREQUENCY, CREATED) VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))" 
        statements = []
        for s in request.form.getlist('site'): #Check through all of the selected sites
            print s
            for kw in request.form['keywords'].split(','): #iterate through our KWs
                #gather them in a list first. That way, if there's a problem with any of them, the whole thing will abort instead of writing partial records
                statements.append({'site'       : str(s),
                                   'keyword'    : str(kw).strip(),
                                   'frequency'  : int(request.form['frequency'])
                    })
        #Now we have a list of statements that we know will work. 
        for st in statements:
            g.db.execute(sql, (str(uuid4()), session['uid'], st['site'], st['keyword'], st['frequency']))
            g.db.commit()

        runs = request.form.getlist('runnow')
        if len(runs)>0 and runs[0] == 'yes':
            #run the most recently added queries and send an email
            print "Running now"
            pass
        if len(statements)>0:
            message = 'Successfully created a new query'
        else:
            message = ''
        return render_template('new_query.html', msg=message)

@app.route('/queries', methods=['GET'])
def queries():
    #show all existing queries for the current user
    #ability to select multiple and run immediately
    pass

@app.route('/newschedule', methods=['POST','GET'])
def newschedule():
    #ability to select a set of queries
    #ability to create a schedule (daily, hourly, etc)
    pass

@app.route('/schedules', methods=['GET'])
def schedules():
    #show all existing schedules for the current user
    #ability to select a schedule and list results from all time, split by runtime
    pass

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