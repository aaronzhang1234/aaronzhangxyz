'''
My website
'''

import pusher
import cgi
import bcrypt
import random
import os.path
import datetime
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import psycopg2
import os.path
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import json

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/recipeimages'

conf = json.load(open('config.json', 'r'))

app.config.update(dict(
    SECRET_KEY=conf['secret_key'],
    USERNAME=conf['username'],
    PASSWORD=conf['password']
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
@app.route('/')
def main_page():
    '''
    Main page of the website
    '''
    return render_template('main_page.html')

@app.route('/morsemessenger')
def morse():
    '''
    This is the main site for morse messenger, if the user is in a channel, the page goes to the send part. If the user is not in the channel, it sends it to the splash page.
    '''
    conn = psycopg2.connect("dbname=morsemessage user=postgres")
    cur = conn.cursor()
    # if user is in a channel or event already, it takes them to the message send screen
    if session.get('channel') and session.get('event'):
        cmd = 'SELECT message FROM message WHERE channel=%s AND event=%s ORDER by id'
        cur.execute(cmd, (session['channel'], session['event']))
        # This gets all the messages sent from the channel.
        morses = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('morsemessenger.html', morses=morses) 
    # IF the user is not in a channel, just send to regular screen
    else:
        return render_template('morsemessenger.html')

@app.route('/morsemessenger/send', methods=['POST'])
def send_morse():
    '''
    When the user sends the message, the message is added to the postgres database and pushed by pusher.
    '''

    # Pusher integration! More info at https://pusher.com
    pusher_client = pusher.Pusher(
        app_id=conf['pusher_id'],
        key=conf['pusher_key'],
        secret=conf['pusher_secret'],
        ssl=True
    )
    conn = psycopg2.connect("dbname=morsemessage user=postgres")
    cur = conn.cursor()
    # Adds the message into the database on the channel and event
    cmd = "insert into message(channel, event,message) values (%s, %s, %s)"
    cur.execute(cmd, (session['channel'], session['event'], request.form['message']))
    conn.commit()
    # Pusher then sends the message through itself to whoever wants it
    pusher_client.trigger(session['channel'], session['event'], {'some':request.form['message']})
    cur.close()
    conn.close()
    return redirect(url_for('morse'))

@app.route('/morsemessenger/join', methods=['POST'])
def joinchannel():
    '''
    When a user joins a channel, it creates sessions variables to see check which channel you are in.
    '''
    session['channel'] = request.form['channel']
    session['event'] = request.form['event']
    session['intalks'] = True
    return redirect(url_for('morse'))

@app.route('/morsemessenger/leave')
def leaveroom():
    '''
    Deletes the session variables set when the user joined the channel
    '''
    session.pop('channel', None)
    session.pop('event', None)
    session.pop('intalks', None)
    return redirect(url_for('morse'))

@app.route('/wikieats')
def wikieats():
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "SELECT recipeid FROM generalrecipes ORDER BY recipeid DESC LIMIT 5"
    cur.execute(cmd)
    new_recipes = cur.fetchall()

    cmd = "SELECT recipeid FROM reviews GROUP BY recipeid ORDER BY AVG(rating) DESC LIMIT 5"
    cur.execute(cmd)
    top_recipes = cur.fetchall()

    cmd = "SELECT reviews.userid FROM reviews LEFT JOIN users ON reviews.userid = users.userid GROUP BY reviews.userid HAVING COUNT(users.userid)>0 ORDER BY COUNT(reviewid) DESC LIMIT 5"
    cur.execute(cmd)
    top_critics = cur.fetchall()

    cmd = "SELECT generalrecipes.userid FROM generalrecipes LEFT JOIN users ON generalrecipes.userid=users.userid GROUP BY generalrecipes.userid HAVING COUNT(users.userid)>0 ORDER BY COUNT(recipeid) DESC LIMIT 5"
    cur.execute(cmd)
    top_chefs = cur.fetchall()

    cmd = "SELECT groupid FROM groupmembers GROUP BY groupid ORDER BY COUNT(userid) DESC LIMIT 5"
    cur.execute(cmd)
    top_groups = cur.fetchall()

    hour = datetime.datetime.now().hour
    if hour>6 and hour<11:
        current_category = 1
    elif hour>11 and hour<14:
        current_category = 2
    elif hour>14 and hour<17:
        current_category = 5
    elif hour>17 and hour<20:
        current_category = 4
    elif hour>20 and hour<22:
        current_category = 4
    else:
        current_category = 5
    cmd = "SELECT recipeid FROM generalrecipes WHERE category = %s"
    cur.execute(cmd, (current_category, ))
    current_recipes = cur.fetchall()
    if not current_recipes:
        current_recipes = []
    else:
        random.shuffle(current_recipes)
        current_recipes = current_recipes[:5]

    cmd = "SELECT categoryname FROM recipecategory WHERE categoryid=%s"
    cur.execute(cmd, (current_category, ))
    category_name = cur.fetchone()

    cmd = "SELECT recipeid FROM generalrecipes"
    cur.execute(cmd)
    random_recipe = cur.fetchall()
    if not random_recipe:
        random_recipe = []
    else:
        random.shuffle(random_recipe)
        random_recipe = random_recipe[:2]

    return render_template('wikieats.html', new_recipes = new_recipes, top_recipes = top_recipes, top_critics = top_critics, top_chefs = top_chefs, top_groups = top_groups, current_recipes = current_recipes, random_recipe=random_recipe, category_name = category_name)

@app.route('/wikieats/about')
def about():
    '''
    Main page of the website
    '''
    return render_template('About.html')

@app.route('/category/<categoryid>', methods=['GET'])
def displaycategory(categoryid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "SELECT categoryname FROM recipecategory WHERE categoryid = %s"
    cur.execute(cmd, (categoryid, ))
    categoryname = cur.fetchone()
    cmd = "SELECT recipeid FROM generalrecipes WHERE category = %s"
    cur.execute(cmd, (categoryid, ))
    recipes = cur.fetchall()
    return render_template('displaycategory.html', recipes=recipes,categoryname=categoryname)

@app.route('/wikieats/createrecipe')
def addrecipepage():
    return render_template('addrecipe.html')

@app.route('/wikieats/createrecipe/create', methods=['POST'])    
def addrecipe():
    app.config['UPLOAD_FOLDER']='static/images/recipeimages'
    conn = psycopg2.connect("dbname=wikieats user=postgres")  
    cur = conn.cursor()
    mainpic = request.files['mainpic']
    mainpicname = secure_filename(mainpic.filename) 
    if mainpicname=="":
        mainpicname = "chefhat.png"
    else:
        cmd = "SELECT last_value FROM generalrecipes_recipeid_seq"
        cur.execute(cmd)
        num = cur.fetchone()
        mainpicnum = num[0]+1
        mainpicname = str(num[0]+1)+'.png'
    mainpic.save(os.path.join(app.config['UPLOAD_FOLDER'],mainpicname))
    cmd = 'INSERT INTO generalrecipes(userid, title, description,category,imagename) VALUES(%s, %s, %s, %s, %s)'
    cur.execute(cmd, (session.get('userid'), cgi.escape(request.form['recipename']), cgi.escape(request.form['description']), request.form['FoodCategory'], mainpicname))
    conn.commit()
    cur.execute('SELECT recipeid FROM generalrecipes ORDER BY recipeid desc LIMIT 1')
    recipeid = cur.fetchone()
    count = 1
    stepnum = 'step'+str(count)
    while count<=len(request.form)-4:
        stepnum = 'step'+str(count)
        imagenum = 'image'+str(count)
        steppic = request.files[imagenum]
        steppicname = secure_filename(steppic.filename)
        if steppic.filename=="":
            steppicname = "chefhat.png"
        else:
            steppicname = str(mainpicnum)+'_'+str(count)+'.png'
        steppic.save(os.path.join(app.config['UPLOAD_FOLDER'], steppicname))
        cmd = 'INSERT INTO recipesteps(recipeid, stepnumber, stepdescription, imagename) VALUES(%s, %s, %s, %s)'
        cur.execute(cmd, (recipeid[0], count, request.form[stepnum], steppicname))
        conn.commit()
        count = count+1
    return redirect(url_for('displayrecipe', recipeid = recipeid[0])) 

@app.route('/wikieats/recipe/<recipeid>', methods=['GET'])
def displayrecipe(recipeid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "SELECT recipeid, userid, title, description, category, imagename, categoryname FROM generalrecipes LEFT JOIN recipecategory ON recipecategory.categoryid = generalrecipes.category WHERE generalrecipes.recipeid = %s"
    cur.execute(cmd, (recipeid, ))
    generalinfo = cur.fetchone()
    cmd = "SELECT username FROM users WHERE userid = %s"
    cur.execute(cmd, (str(generalinfo[1]), ))
    username = cur.fetchone()
    cmd = "SELECT stepnumber,stepdescription, imagename FROM recipesteps WHERE recipeid = %s "
    cur.execute(cmd, (recipeid, ))
    steps = cur.fetchall()
    cmd = "SELECT reviewtitle,reviewtext,rating,reviews.userid FROM reviews WHERE recipeid = %s"
    cur.execute(cmd, (recipeid, ))
    reviews = cur.fetchall()
    category = generalinfo[4]
    cmd = "SELECT recipeid FROM generalrecipes WHERE (recipeid <> %s AND (userid=%s OR category= %s))"
    cur.execute(cmd, (recipeid, generalinfo[1], category))
    related_recipes = cur.fetchall()
    is_already_pinned = False
    if session.get('userid'):
        cmd = "SELECT groupid, groupname FROM groups WHERE leaderid = %s"
        cur.execute(cmd, (session.get('userid'), ))

        head_of_groups = cur.fetchall()
        cmd = "SELECT * FROM pinnedrecipes LEFT JOIN groups on groups.groupid = pinnedrecipes.groupid WHERE leaderid = %s AND recipeid = %s"
        cur.execute(cmd, (session.get('userid') , recipeid))
        if len(cur.fetchall()) > 0:
            is_already_pinned = True
    else:
        head_of_groups = False
    cmd = "SELECT AVG(rating) FROM reviews WHERE recipeid = %s GROUP BY recipeid"
    cur.execute(cmd, (recipeid, ))
    average_rating = cur.fetchone()
    if average_rating is None:
        average_rating = '~'
    else:
        average_rating = int(average_rating[0])
    return render_template('displayrecipe.html', generalinfo=generalinfo, steps=steps, reviews=reviews, is_already_pinned = is_already_pinned, head_of_groups=head_of_groups, average_rating=average_rating, related_recipes=related_recipes, username=username)

@app.route('/wikieats/recipe/<recipeid>/pinrecipe', methods=['POST'])
def pinRecipe(recipeid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "INSERT INTO pinnedrecipes(groupid, recipeid) VALUES (%s, %s)"
    cur.execute(cmd, (request.form['pin'], recipeid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))
    
@app.route('/wikieats/groups/<groupid>/<recipeid>/unpinrecipe', methods=['POST'])
def unpinRecipe(recipeid, groupid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "DELETE FROM pinnedrecipes WHERE recipeid=%s AND groupid=%s"
    cur.execute(cmd, (recipeid, groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))

@app.route('/wikieats/recipe/<recipeid>/reviewrecipe', methods=['POST'])
def reviewrecipe(recipeid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "INSERT INTO reviews (recipeid,reviewtitle,reviewtext,userid,rating) VALUES(%s,%s,%s,%s,%s)"
    cur.execute(cmd, (recipeid, cgi.escape(request.form['Title']), cgi.escape(request.form['review']), session.get('userid'), request.form['rating']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))

@app.route('/wikieats/review/<reviewid>/deletereview', methods=['POST'])
def deletereview(reviewid):
    conn = psycopg2.connect("dbname = wikieats user=postgres")
    cur = conn.cursor()
    cmd = "DELETE FROM reviews WHERE reviewid = %s"
    cur.execute(cmd, (reviewid, ))
    conn.commit()
    return redirect(url_for('displayuser', userid = session.get('userid')))

@app.route('/wikieats/user/<userid>', methods=['GET'])
def displayuser(userid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "SELECT userid,username,firstname,lastname from users WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    userinfo = cur.fetchone()

    cmd = "SELECT recipeid FROM generalrecipes WHERE userid=%s"
    cur.execute(cmd, (userid, ))
    userrecipes = cur.fetchall()

    cmd = "SELECT followingid FROM following WHERE followerid = %s"
    cur.execute(cmd, (userid, ))
    following = cur.fetchall()

    cmd = "SELECT followerid FROM following WHERE followingid = %s"
    cur.execute(cmd, (userid, ))
    followers = cur.fetchall()

    cmd = "SELECT groupid FROM groupmembers WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    groups = cur.fetchall()

    cmd = "SELECT reviewid,generalrecipes.recipeid,reviewtitle,reviewtext,rating,title,description,category,categoryname,generalrecipes.userid,username FROM reviews LEFT JOIN generalrecipes ON reviews.recipeid = generalrecipes.recipeid LEFT JOIN recipecategory ON generalrecipes.category = recipecategory.categoryid LEFT JOIN users ON generalrecipes.userid = users.userid WHERE reviews.userid = %s"
    cur.execute(cmd, (userid, ))
    reviews = cur.fetchall()

    return render_template('displayuser.html', userinfo=userinfo, userrecipes=userrecipes, following=following, followers=followers, groups=groups, reviews=reviews)

@app.route('/wikieats/user/<followingid>/follow', methods=['POST'])
def followUser(followingid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "INSERT INTO following (followerid, followingid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), followingid))
    conn.commit()
    return redirect(url_for('displayuser', userid=followingid))

@app.route('/wikieats/user/<followingid>/unfollow', methods=['POST'])
def unfollowUser(followingid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "DELETE FROM following WHERE followingid = %s AND followerid = %s"
    cur.execute(cmd, (followingid, session.get('userid')))
    conn.commit()
    return redirect(url_for('displayuser', userid=followingid))

@app.route('/wikieats/user/<userid>/manage', methods=['POST'])
def changeaccount(userid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    firstname = cgi.escape(request.form['firstname'])
    lastname = cgi.escape(request.form['lastname'])
    newUsername = cgi.escape(request.form['newusername'])
    newPassword = request.form['newpassword']
    oldPassword = request.form['password'].encode('utf-8')
    cmd = "SELECT password, userid FROM users WHERE userid =%s"
    cur.execute(cmd, (userid, ))
    user = cur.fetchone()
    password = user[0].encode('utf-8')
    if not bcrypt.checkpw(oldPassword, password):
        session['error'] = True
        return redirect(url_for('displayuser', userid=userid))
    session['error'] = False
    if firstname:
        cmd = "UPDATE users SET firstname=%s WHERE userid = %s"
        cur.execute(cmd, (firstname, userid))
        conn.commit()
    if lastname:
        cmd = "UPDATE users SET lastname=%s WHERE userid = %s"
        cur.execute(cmd, (lastname, userid))
        conn.commit()
    if newUsername:
        cmd = "SELECT username FROM users WHERE username = %s"
        cur.execute(cmd, (newUsername, ))
        if cur.fetchone():
            session['usernametaken'] = True
            return redirect(url_for('displayuser', userid=userid))
        session['usernametaken'] = False
        cmd = "UPDATE users SET username=%s WHERE userid=%s"
        cur.execute(cmd, (newUsername, userid))
        conn.commit()
    if newPassword:
        cmd = "UPDATE users SET password=%s WHERE userid=%s"
        cur.execute(cmd, (newPassword, userid))
        conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayuser', userid=userid))
    

@app.route('/wikieats/user/<userid>/delete', methods=['POST'])
def deleteaccount(userid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()

    cmd = "SELECT groupid FROM groups WHERE leaderid=%s"
    cur.execute(cmd, (str(userid), ))
    groupsled = cur.fetchall()
    for group in groupsled:
        cmd = "DELETE FROM groupmembers WHERE groupid = %s"
        cur.execute(cmd, (str(group[0]), ))
        conn.commit()
    cmd = "DELETE FROM groups WHERE leaderid =%s"
    cur.execute(cmd, (userid, ))
    conn.commit()
    cmd = "DELETE FROM users WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    conn.commit()
    cur.close()
    conn.close()
    session.pop('userid', None)
    return redirect(url_for('loginpage'))

@app.route('/wikieats/login')
def loginpage():
    if session.get('userid'):
        return redirect(url_for('wikieats'))

    return render_template('login.html')

@app.route('/wikieats/login/login', methods=['POST'])
def login():
    if session.get('userid'):
        return redirect(url_for('page_not_found'))
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    passwordencoded = request.form['password'].encode('utf-8')
    cmd = 'SELECT password,userid FROM users WHERE username=%s'
    cur.execute(cmd, (request.form['username'], ))
    password = cur.fetchone()
    if password:
        userid = password[1]
        password = password[0].encode('utf-8')
        if bcrypt.checkpw(passwordencoded, password):
            session['userid'] = userid
            session['error'] = False
            return redirect(url_for('wikieats'))
        else:
            session['error'] = True
            return redirect(url_for('loginpage'))
    else:
        session['error'] = True
        return redirect(url_for('loginpage'))

@app.route('/wikieats/logout')
def logout():
    session.pop('userid', None)
    return redirect(url_for('wikieats'))

@app.route('/wikieats/createaccount')
def createaccountpage():
    if session.get('userid'):
        return redirect(url_for('wikieats'))
    return render_template('createaccount.html')

@app.route('/wikieats/createaccount/create', methods=['POST'])
def createaccount():
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = 'SELECT userid FROM users WHERE username = %s'
    cur.execute(cmd, (request.form['username'],))
    if cur.fetchone() is not None or request.form['verification'] != conf['wikieatsjoin']:
        return redirect(url_for('createaccountpage'))
        session['error'] = True
    else:
        session['error'] = False
        cmd = "INSERT INTO users (username, firstname, lastname, password) VALUES (%s, %s, %s, %s)"
        passwordencoded = request.form['password1'].encode('utf-8')
        passwordbcrypt = bcrypt.hashpw(passwordencoded, bcrypt.gensalt()).decode('utf-8')
        cur.execute(cmd, (cgi.escape(request.form['username']),cgi.escape(request.form['fName']), cgi.escape(request.form['lName']), passwordbcrypt))
        conn.commit()
        cmd = "SELECT userid FROM users ORDER BY userid DESC LIMIT 1"
        cur.execute(cmd)
        userid = cur.fetchone()
        session['userid'] = userid[0]
        return redirect(url_for('displayuser',userid=userid[0]))

@app.route('/wikieats/creategroup')
def creategrouppage():
    return render_template('creategroup.html')

@app.route('/wikieats/group/<groupid>', methods=['GET'])
def displaygroup(groupid):
    conn = psycopg2.connect("dbname=wikieats user=postgres")
    cur = conn.cursor()
    cmd = "SELECT recipeid FROM pinnedrecipes WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    pinnedrecipes = cur.fetchall()
    cmd = "SELECT recipeid FROM generalrecipes LEFT JOIN groupmembers ON groupmembers.userid = generalrecipes.userid WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    grouprecipes = cur.fetchall()
    cmd = "SELECT groupid, groupname, groupdescription, leaderid, grouppicture FROM groups WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    groupinfo = cur.fetchone()
    cmd = "SELECT users.userid, username FROM groupmembers LEFT JOIN users on groupmembers.userid = users.userid WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    groupmembers = cur.fetchall()
    return render_template('displaygroup.html', pinnedrecipes = pinnedrecipes, grouprecipes = grouprecipes, groupinfo = groupinfo, groupmembers = groupmembers)

@app.route('/wikieats/creategroup/create', methods=['POST'])
def creategroup():
    app.config['UPLOAD_FOLDER']='static/images/grouppics'
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    grouppic = request.files['grouppic']
    grouppicname = secure_filename(grouppic.filename)
    if grouppic.filename=="":
        grouppicname = "chef_hat.png"
    else:
        grouppic.save(os.path.join(app.config['UPLOAD_FOLDER'], grouppicname))
    cmd = "INSERT INTO groups (groupname, groupdescription, leaderid, grouppicture) VALUES (%s, %s, %s, %s)"
    cur.execute(cmd, (cgi.escape(request.form['groupname']), cgi.escape(request.form['groupdesc']), session.get('userid'), grouppicname))
    conn.commit()
    cmd = "SELECT groupid FROM groups ORDER BY groupid DESC LIMIT 1"
    cur.execute(cmd)
    groupid = cur.fetchone()
    cmd = "INSERT INTO groupmembers (userid, groupid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), groupid[0]))
    conn.commit()
    return redirect(url_for('displaygroup', groupid = groupid[0]))

@app.route('/wikieats/group/<groupid>/leave', methods=['POST'])
def leavegroup(groupid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "DELETE FROM groupmembers WHERE userid = %s AND groupid = %s"
    cur.execute(cmd, (session.get('userid'), groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid = groupid))

@app.route('/wikieats/group/<groupid>/join', methods=['POST'])
def joingroup(groupid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "INSERT INTO groupmembers (userid, groupid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid = groupid))

@app.route('/wikieats/group/<groupid>/delete')
def deletegroup(groupid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "DELETE FROM groups WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    conn.commit()
    cmd = "DELETE FROM groupmembers WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('about'))

@app.route('/wikieats/group/<groupid>/manage', methods=['POST'])
def managegroup(groupid):
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "UPDATE groups SET leaderid = %s WHERE groupid = %s"
    cur.execute(cmd, (request.form['transfer'], groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid=groupid))

@app.route('/wikieats/search', methods=['GET'])
def search():
    search = cgi.escape(request.args.get('search'))
    searchparen = '%'+search+'%'
    conn = psycopg2.connect('dbname=wikieats user=postgres')
    cur = conn.cursor()
    cmd = "SELECT recipeid FROM generalrecipes WHERE title LIKE %s"
    cur.execute(cmd, (searchparen, ))
    searchrecipes = cur.fetchall()
    cmd = "SELECT userid FROM users WHERE username LIKE %s"
    cur.execute(cmd, (searchparen, ))
    searchusers = cur.fetchall()
    return render_template('searchrecipe.html', searchrecipes=searchrecipes, searchusers=searchusers, search=search)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
