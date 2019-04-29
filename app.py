from flask import Flask, render_template, url_for, session, request, redirect, g, flash, get_flashed_messages

import os
import smtplib
import sqlite3

import time

DATABASE = 'compatability.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


#@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=()):


    cur = get_db().execute(query, args)


    rv = cur.fetchall()
    cur.close()
    #return (rv[0] if rv else None) if one else rv
    return rv


app = Flask(__name__)
#@app.run(host='0.0.0.0')



@app.route("/", methods=["GET", "POST"])

def index():

    if request.method == "POST":
        username=request.form.get("username")
        password = request.form.get("password")
        if request.form.get("username")=="oprah" and request.form.get("password")=="cats":
             return render_template("index.html")

        else:
            query = 'select * from accounts where username = "' + username + '" and password = "' + password +'"'
            user = query_db(query)
            if not user:
                print ('No such user')
                return render_template("oops.html")

            else:
                userid=user[0][0] #unique user id
                session['username'] = user[0][1] #store user name as session variable
                session['id']=userid #store as session variable
                return render_template("index.html")



    else:
          return render_template("index.html")

@app.route('/login')
def login():
    """ Displays the page greats who ever comes to visit it.
    """
    return render_template('login.html')

@app.route('/create', methods=["GET", "POST"])
def create():


    if request.method == "POST":

        username=request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        age = request.form.get("age")

        user = query_db('insert into accounts ("name","username","password","age") VALUES (?,?,?,?)', (name, username,password,age))
        get_db().commit()

        flash('You Succesfully Created an Account')
        time.sleep(3)

        return render_template("login.html")

    else: #get request
        return render_template("create.html")

@app.route('/survey', methods=["GET", "POST"])
def survey():

    print("HERE-----------------------------")
    if request.method == "POST":
        print("HERE-----------------------------")

        #add to sql survey table
        text = request.form.get("most")
        if text == "party":
          score1 = 1
        elif text == "health":
          score1 = 2
        elif text == "earth":
          score1 = 4
        else:
            score1 = 3

        #add to sql survey table
        text = request.form.get("m1")
        if text == "ariz":
          score1 = score1 + 1
        elif text == "mich":
          score1 = score1 + 2
        elif text == "duke":
          score1 = score1 + 4
        else:
            score1 = score1 + 3

        score1 = score1 / 2.0
        score1 = round(score1)
        score1 = int(score1)
        print("-----------")
        print(score1)

        time.sleep(8)

        id = session['id'] #store the id of the person currently logged in (our session variable, in the table with their personality test score
        user = query_db('insert into surveyinfo ("userid", "score1") VALUES (?,?)', (id, score1))
        get_db().commit()

        return render_template('index.html')

    else: #get request, if user is logged in (username in session - show them the survey, otherwise send to login page)
        if 'username' in session:

            return render_template("survey.html")
        else:
            return render_template("login.html")

@app.route('/thoughts', methods=["GET", "POST"])
def thoughts():
    print("LETS TRY SOMETHING NEW")

    if request.method == "POST":
        quizScore = 0
        text1 = request.form.get("red")
        print(text1)

        if text1 == "rick":
            quizScore = quizScore + 1

        text2 = request.form.get("pats")

        if text2 == "danny":
            quizScore = quizScore + 1

        text3 = request.form.get("celtics")
        if text3 == "robert":
            quizScore = quizScore + 1

        quizScore = str(quizScore)
        print(quizScore)

        id = session['id'] #get id of currently logged in user so this id can be stored in the thoughts table with their thought
        user = query_db('insert into thoughts ("accountOwner", "thoughts") VALUES (?,?)', (id, quizScore))
        get_db().commit()
        return render_template("index.html")

    else:

        if 'username' in session: #if user is logged in, get all their previous thoughts using their session id and querying thoughts table with it
            id = session['id']
            id = str(id)
            query = 'select thoughts from thoughts where accountOwner = "' + id + '"'
            msgs = query_db(query)
            options={}
            if not msgs:
                send = "none"

            else: #build a string of all their thoughts that were returned from table, to send as variable to thoughts.html
                send=""
                i=0
                for tht in msgs:
                    send += tht[0] + '\n'

            return render_template("thoughts.html", msg=send)
        else:
            return render_template("login.html") #if not logged in, render login page

@app.route('/friends', methods=["GET", "POST"])
def friends():

    if request.method == "POST":
        text = request.form.get("message")
        id = session['id']
        user = query_db('insert into thoughts ("accountOwner", "thoughts") VALUES (?,?)', (id, text))
        get_db().commit()

        return render_template("index.html")

    else:

        if 'username' in session:
            id = request.args["var"] #this was a get request, var and name are part of the URL when built in url_for, see friends.html
            name = request.args["name"]

            id = str(id)
            query = 'select thoughts from thoughts where accountOwner = "' + id + '"' #find the thoughts of this "friend's" id

            msgs = query_db(query)
            options={}
            if not msgs:
                send = "none"

            else:
                send=""
                i=0

                for tht in msgs:
                    send += tht[0] + '\n'


            return render_template("friendsthoughts.html", msg=send, name=name)
        else:
            return render_template("login.html")

@app.route('/matches', methods=["GET", "POST"])
def matches():


    if request.method == "POST":
        text = request.form.get("message")
        id = session['id']
        user = query_db('insert into thoughts ("accountOwner", "thoughts") VALUES (?,?)', (id, text))
        get_db().commit()




        return render_template("index.html")

    else:

        if 'username' in session:
            id = session['id']
            id = str(id)
            query = 'select score1 from surveyinfo where userid = "' + id + '"'

            msgs = query_db(query)
            idlist=""

            if not msgs:
                return render_template("survey.html")

            print(query)
            print(msgs[len(msgs)-1][0])

            surv_score = str(msgs[len(msgs)-1][0])
            print(surv_score)

            if surv_score == "1":
                return render_template("gronk.html")

            elif surv_score == "2":
                return render_template("brady.html")

            elif surv_score == "4":
                return render_template("kyrie.html")

            else:
                return render_template("chara.html")
            # if not msgs:
            #
            #     send = "You have no matches because you didn't take the survey"
            # else:
            #     send=""
            #
            #
            #     yourscore = msgs[0][0]
            #     yourscore = str(yourscore)
            #     query2 = 'select userid from surveyinfo where score1 = "' + yourscore + '"'
            #
            #     matches = query_db(query2)
            #
            #     for match in matches:
            #         matchid = str(match[0])
            #         if matchid != id:
            #             query3 = 'select name from accounts where uniqueId = "' + matchid + '"'
            #             user = query_db(query3)
            #             send += user[0][0] + '\n'
            #             idlist += matchid + ';'
            #     print(send)
            # return render_template("matches.html", msg=send, ids=idlist)
        else:
            return render_template("login.html")


@app.route('/logout')
def logout():

   session.pop('username', None) #removes username from session variable
   session.pop('id', None) #no longer logged in
   return render_template("index.html")

@app.route('/leaderboard', methods=["GET"])
def leaderboard():
    if 'username' in session:
        print("------------------------")
        id = session['id']
        id = str(id)
        query = 'SELECT MAX(thoughts) FROM thoughts'

        msgs = query_db(query)
        print(msgs[0][0])
        send = str(msgs[0][0])
        # idlist=""
        #
        # if not msgs:
        #     send = "You have no matches because you didn't take the survey"
        # else:
        #     send=""
        #
        #
        # yourscore = msgs[0][0]
        # yourscore = str(yourscore)
        # query2 = 'select userid from surveyinfo where score1 = "' + yourscore + '"'
        #
        # matches = query_db(query2)
        #
        # for match in matches:
        #     matchid = str(match[0])
        #     if matchid != id:
        #         query3 = 'select name from accounts where uniqueId = "' + matchid + '"'
        #         user = query_db(query3)
        #         send += user[0][0] + '\n'
        #         idlist += matchid + ';'
        #         print(send)
        return render_template("matches.html", msg=send)
    else:
        return render_template("login.html")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #needed to use sessions
