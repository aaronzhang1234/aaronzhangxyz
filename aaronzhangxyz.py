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
app.config['UPLOAD_FOLDER'] = '/home/centralcommand/aaronzhangxyz/static/images/recipeimages'
conf = json.load(open('config.json', 'r'))
app.config.update(dict(
    SECRET_KEY=conf['secret_key'],
    USERNAME=conf['username'],
    PASSWORD=conf['password']
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
@app.context_processor
def my_utility_processor():
    '''
    All the Functions that need to be iterated over multiple times and are dynamic. Displaying small things.
    '''
    def printrecipe(recipeid):
        '''
        Prints out a recipe but in a smaller form
        '''
        conn = psycopg2.connect("dbname=wikieats user=aaron")
        cur = conn.cursor()
        cmd = "SELECT recipeid, generalrecipes.userid, title, description, category, imagename, categoryname FROM generalrecipes LEFT JOIN recipecategory ON recipecategory.categoryid = generalrecipes.category WHERE generalrecipes.recipeid = %s"
        cur.execute(cmd, (recipeid, ))
        recipe = cur.fetchone()
        cmd = "SELECT AVG(rating) FROM reviews GROUP BY recipeid HAVING recipeid = %s"
        cur.execute(cmd, (recipeid, ))
        averagerating = cur.fetchone()
        if averagerating is None:
            averagerating='~'
        else:
            averagerating = int(averagerating[0])
        cmd = "SELECT username FROM users WHERE userid = %s"
        cur.execute(cmd, (recipe[1], ))
        username = cur.fetchone()
        userinfo =""
        if username:
            userinfo = '<a href="'+url_for("displayuser", userid=str(recipe[1]))+'">'+str(username[0])+'</a>'
        else:
            userinfo = 'deleted'
        return '<div class="col-md-12 panel"><div class = "col-md-12"><h2><a href="'+url_for("displayrecipe", recipeid =str(recipe[0]))+'">'+str(recipe[2])+ ' </a> <small>(<a href = "'+url_for("displaycategory", categoryid = str(recipe[4])) +'">'+str(recipe[6])+' </a>) by '+userinfo+' </small></h2></div><div class="col-md-4"><img src="../../static/images/recipeimages/'+str(recipe[5])+'" alt="'+str(recipe[2])+'" class="img-thumbnail" /></div><div class="col-md-8"><h4>'+str(averagerating)+'/5</h4><p>'+str(recipe[3])+'</p></div></div><hr>'
    def isPinned(groupid, recipeid):
        '''
        Takes a group and a recipe and returns True if the recipe is pinned or False if not
        '''
        conn = psycopg2.connect("dbname=wikieats user=aaron")
        cur = conn.cursor()
        cmd = "SELECT * FROM pinnedrecipes WHERE groupid = %s and recipeid=%s"
        cur.execute(cmd, (groupid, recipeid))
        pinned_recipe = cur.fetchone()
        if pinned_recipe is None:
            return False
        else:
            return True
    def printstep(step):
        return '<div class="row"><div class="col-md-12 col-md-offset-1"><h2>Step'+ str(step[0])+'</h2></div><div class="col-md-3 col-md-offset-1"><img src="../../static/images/recipeimages/'+step[2]+'" alt="'+step[2]+'" class="img-responsive"/></div><div class="col-md-5"><p style="font-size:1.5em;">'+step[1]+'</p></div></div>'
    def printreview(review):
        '''
        Prints review, self explanatory
        '''
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT username FROM users WHERE userid=%s"
        cur.execute(cmd, (review[3], ))
        username = cur.fetchone()
        if username:
            userinfo = '<a href="'+url_for("displayuser", userid=str(review[3]))+'">'+username[0]+'</a>'
        else:
            userinfo = 'deleted'
        return '<div class="col-md-12-panel"><h2 class="col-md-2">'+str(review[2])+'/5</h2><div class="col-md-10"><h3>'+review[0]+'</h3><h4>' +userinfo+' </h4></div><p>'+review[1]+'</p></div><hr>'
    def isLeader(groupid, userid):
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT * FROM groups WHERE groupid = %s AND leaderid = %s"
        cur.execute(cmd, (groupid, userid))
        groupLeader = cur.fetchone()
        if groupLeader is None:
            return False;
        else:
            return True;
    def inGroup(groupid, userid):
        '''
        Takes a user and a group and sees if the User is in the group
        '''
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT * FROM groupmembers WHERE groupid = %s AND userid=%s"
        cur.execute(cmd, (groupid, userid))
        groupMember = cur.fetchone()
        if groupMember is None:
            return False;
        else:
            return True;
    def printgroup(groupid):
        '''
        Prints groups in a compact way, used multiple times
        '''
        conn = psycopg2.connect('dbname = wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT groupid, groupname, groupdescription, grouppicture FROM groups WHERE groupid = %s"
        cur.execute(cmd, (groupid, ))
        group = cur.fetchone()
        return '<div class = "col-md-12 panel"><div class="col-md-4"><img src="../../static/images/grouppics/'+ str(group[3]) +'" alt="'+str(group[1])+'" class="img-thumbnail"/> </div><div class="col-md-8"><h3><a href="'+ url_for('displaygroup',groupid=groupid)+'">'+str(group[1])+'</a></h3><p>'+str(group[2])+'</p></div></div><hr/>'
    def printuser(user):
        '''
        Takes userid and prints out the user.
        '''
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT COUNT(recipeid) FROM generalrecipes GROUP BY userid HAVING userid=%s"
        cur.execute(cmd, (user, ))
        numRecipes = cur.fetchone()
        if numRecipes is None:
            numRecipes = 0
        else:
            numRecipes = numRecipes[0]
        cmd = "SELECT username FROM users WHERE userid = %s"
        cur.execute(cmd, (user, ))
        username = cur.fetchone()
        cmd = "SELECT COUNT(reviewid) FROM reviews GROUP BY userid HAVING userid = %s"
        cur.execute(cmd, (user, ))
        numReviews = cur.fetchone()
        if numReviews is None:
            numReviews = 0
        else:
            numReviews = numReviews[0]
        return '<div class="col-md-12 panel"><h2 class="col-md-12"><a href="'+ url_for('displayuser', userid=str(user)) +'">'+ str(username[0]) +'</a></h2><div class="col-md-6">'+ str(numRecipes) +' Submitted Recipes</div><div class="col-md-6">'+ str(numReviews) +' Reviews</div></div><hr/>'
    def isFollowing(followingid, followerid):
        '''
        Checks to see if followingid is following followerid
        Returns True if is following
        '''
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT * FROM following WHERE followingid = %s AND followerid=%s"
        cur.execute(cmd, (followingid, followerid))
        following = cur.fetchone()
        if following is None:
            return False
        else:
            return True
    def printcarousel(recipeid, active=""):
        '''
        Prints the carousel in the main page of the website.
        '''
        conn = psycopg2.connect('dbname=wikieats user=aaron')
        cur = conn.cursor()
        cmd = "SELECT title, description, imagename FROM generalrecipes WHERE recipeid = %s"
        cur.execute(cmd, (recipeid, ))
        recipe = cur.fetchone()
        return '<div class="item'+active+'"><img style="display:block;margin:auto;width:90%" src="../static/images/recipeimages/'+recipe[2]+'" alt="'+recipe[0]+'" width="500" height="345"><div class="carousel-caption"><h3>'+recipe[0]+'</h3><p>'+recipe[1]+'</p></div></div>'
    return dict(printrecipe=printrecipe, printstep=printstep, printreview=printreview,isPinned=isPinned, isLeader=isLeader, inGroup=inGroup, printuser=printuser, isFollowing=isFollowing, printgroup=printgroup, printcarousel=printcarousel) 
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
    conn = psycopg2.connect("dbname=morsemessage user=aaron")
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
    conn = psycopg2.connect("dbname=morsemessage user=aaronadd")
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
    '''
    Main page for wikieats, this functions gets all the quick overview of the site.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aaron')
    cur = conn.cursor()
    # Selects 5 newest recipes  
    cmd = "SELECT recipeid FROM generalrecipes ORDER BY recipeid DESC LIMIT 5"
    cur.execute(cmd)
    new_recipes = cur.fetchall()
    # Selects Top 5 best recipes grouped by average review
    cmd = "SELECT recipeid FROM reviews GROUP BY recipeid ORDER BY AVG(rating) DESC LIMIT 5"
    cur.execute(cmd)
    top_recipes = cur.fetchall()
    # Selects the Top 5 people who have made the most reviews
    cmd = "SELECT reviews.userid FROM reviews LEFT JOIN users ON reviews.userid = users.userid GROUP BY reviews.userid HAVING COUNT(users.userid)>0 ORDER BY COUNT(reviewid) DESC LIMIT 5"
    cur.execute(cmd)
    top_critics = cur.fetchall()
    # Selects the Top 5 people who have made the most recipes
    cmd = "SELECT generalrecipes.userid FROM generalrecipes LEFT JOIN users ON generalrecipes.userid=users.userid GROUP BY generalrecipes.userid HAVING COUNT(users.userid)>0 ORDER BY COUNT(recipeid) DESC LIMIT 5"
    cur.execute(cmd)
    top_chefs = cur.fetchall()
    # Selects the Top 5 Groups by most amount of members joined
    cmd = "SELECT groupid FROM groupmembers GROUP BY groupid ORDER BY COUNT(userid) DESC LIMIT 5"
    cur.execute(cmd)
    top_groups = cur.fetchall()
    # This else if statement block gets the time and returns a corresponding category for the time.
    # Used to create a website that molds to your needs
    hour = datetime.datetime.now().hour
    if hour > 6 and hour < 11:
        current_category = 1
    elif hour > 11 and hour < 14:
        current_category = 2
    elif hour > 14 and hour < 17:
        current_category = 5
    elif hour > 17 and hour < 20:
        current_category = 4
    elif hour > 20 and hour < 22:
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
    # Next few lines are getting 2 random recipes from the entire pot
    cmd = "SELECT recipeid FROM generalrecipes"
    cur.execute(cmd)
    random_recipe = cur.fetchall()
    if not random_recipe:
        random_recipe = []
    else:
        random.shuffle(random_recipe)
        random_recipe = random_recipe[:2]
    # Creating the website itself with all the necessary variables
    return render_template('wikieats.html', new_recipes=new_recipes, top_recipes=top_recipes, top_critics=top_critics, top_chefs=top_chefs, top_groups=top_groups, current_recipes=current_recipes, random_recipe=random_recipe, category_name=category_name)
@app.route('/wikieats/about')
def about():
    '''
    About site of wikieats, info about the creators.
    '''
    return render_template('About.html')
@app.route('/category/<categoryid>', methods=['GET'])
def displaycategory(categoryid):
    '''
    Displays Category and all the recipes in that said category
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaron")
    cur = conn.cursor()
    # Getting category name from the id
    cmd = "SELECT categoryname FROM recipecategory WHERE categoryid = %s"
    cur.execute(cmd, (categoryid, ))
    categoryname = cur.fetchone()
    # Getting all recipes from the category specified
    cmd = "SELECT recipeid FROM generalrecipes WHERE category = %s"
    cur.execute(cmd, (categoryid, ))
    recipes = cur.fetchall()
    return render_template('displaycategory.html', recipes=recipes, categoryname=categoryname)
@app.route('/wikieats/createrecipe')
def addrecipepage():
    '''
    Page for the form where you add the recipe
    '''
    return render_template('addrecipe.html')
    
@app.route('/wikieats/createrecipe/create', methods=['POST'])
def addrecipe():
    '''
    Actually uploading the recipe and storing it into a database
    '''
    allowed_extensions = ['jpeg', 'jpg', 'png']
    app.config['UPLOAD_FOLDER']='static/images/recipeimages'   #Place where recipe images are saved
    conn = psycopg2.connect("dbname=wikieats user=aaronadd")  
    cur = conn.cursor()
    session['right_extension'] = True
    mainpic = request.files['mainpic']
    mainpicname = secure_filename(mainpic.filename) 
    # If the user didn't upload a picture then put the default one in
    cmd = "SELECT last_value FROM generalrecipes_recipeid_seq"
    cur.execute(cmd)
    num = cur.fetchone()
    mainpicnum = num[0]+1
    if mainpicname=="":
        mainpicname = "chefhat.png"
    else:
        pic_array = mainpicname.split('.')
        extension = pic_array[-1]
        if extension not in allowed_extensions:
            session['right_extension'] = False
            return redirect(url_for('addrecipepage'))
        # Rename the picture to the recipeid it will be, this SQL command is selecting the next recipeid as a number
        mainpicname = str(num[0]+1)+'.png'
    # Actually saving the picture in the path
    mainpic.save(os.path.join(app.config['UPLOAD_FOLDER'],mainpicname))
    # Inserting the recipe information into the database
    cmd = 'INSERT INTO generalrecipes(userid, title, description,category,imagename) VALUES(%s, %s, %s, %s, %s)'
    cur.execute(cmd, (session.get('userid'), cgi.escape(request.form['recipename']), cgi.escape(request.form['description']), request.form['FoodCategory'], mainpicname))
    conn.commit()
    cur.execute('SELECT recipeid FROM generalrecipes ORDER BY recipeid desc LIMIT 1')
    # Getting the recipeid
    recipeid = cur.fetchone()
    count = 1
    # The reason why this whileloop is going from 1 to whatever the len-4 is because there are four other elements in the form other than the steps
    # A generally bruteforcing way
    while count <=len(request.form)-4:
        # This is getting the name of the form input so it can request the data
        stepnum = 'step'+str(count)
        imagenum = 'image'+str(count)
        stepdescription = request.form[stepnum]
        # Generally the same image upload as last time
        steppic = request.files[imagenum]
        steppicname = secure_filename(steppic.filename)
        if steppic.filename =="":
            steppicname = "chefhat.png"
        else:
            #pic_array = steppicname.split('.')
            #extension = pic_array[-1]
            #if extension not in allowed_extensions:
            #    session['right_extension'] = False
            #    return redirect(url_for('addrecipepage'))
            # However this is renaming the image to the recipeid plus an underscore and the stepid
            # Step 2 in recipe #4  will be renamed 4_2  
            steppicname = str(mainpicnum)+'_'+str(count)+'.png'
        steppic.save(os.path.join(app.config['UPLOAD_FOLDER'], steppicname))
        # Inserting the information into the database
        cmd = 'INSERT INTO recipesteps(recipeid, stepnumber, stepdescription, imagename) VALUES(%s, %s, %s, %s)'
        cur.execute(cmd, (recipeid[0], count, stepdescription, steppicname))
        conn.commit()
        count = count+1
    return redirect(url_for('displayrecipe', recipeid = recipeid[0]))
@app.route('/wikieats/recipe/<recipeid>', methods=['GET'])
def displayrecipe(recipeid):
    '''
    Displaying a recipe, this time the actual page of the recipe itself.
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaron")
    cur = conn.cursor()
    # Getting recipe info such as title, user who made it, description etc..
    cmd = "SELECT recipeid, userid, title, description, category, imagename, categoryname FROM generalrecipes LEFT JOIN recipecategory ON recipecategory.categoryid = generalrecipes.category WHERE generalrecipes.recipeid = %s"
    cur.execute(cmd, (recipeid, ))
    generalinfo = cur.fetchone()
    # Getting the username of the user who made the recipe
    cmd = "SELECT username FROM users WHERE userid = %s"
    cur.execute(cmd, (str(generalinfo[1]), ))
    username = cur.fetchone()
    # Getting all the steps for the recipe
    cmd = "SELECT stepnumber,stepdescription, imagename FROM recipesteps WHERE recipeid = %s "
    cur.execute(cmd, (recipeid, ))
    steps = cur.fetchall()
    # Getting all reviews made for this recipe
    cmd = "SELECT reviewtitle,reviewtext,rating,reviews.userid FROM reviews WHERE recipeid = %s"
    cur.execute(cmd, (recipeid, ))
    reviews = cur.fetchall()
    # Related recipes either means recipes that the same user has made or recipes in the same category
    category = generalinfo[4]
    cmd = "SELECT recipeid FROM generalrecipes WHERE (recipeid <> %s AND (userid=%s OR category= %s))"
    cur.execute(cmd, (recipeid, generalinfo[1], category))
    related_recipes = cur.fetchall()
    is_already_pinned = False
    # This is seeing if the user is the head of a group and if the user then seeing if the recipe is pinned
    # head_of_groups is going to be used for pinning recipes to groups
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
    # Getting the average rating of the recipe
    cmd = "SELECT AVG(rating) FROM reviews WHERE recipeid = %s GROUP BY recipeid"
    cur.execute(cmd, (recipeid, ))
    average_rating = cur.fetchone()
    # If no one has reviewed the recipe, the average rating is just ~
    if average_rating is None:
        average_rating = '~'
    else:
        average_rating = int(average_rating[0])
    return render_template('displayrecipe.html', generalinfo=generalinfo, steps=steps, reviews=reviews, is_already_pinned=is_already_pinned, head_of_groups=head_of_groups, average_rating=average_rating, related_recipes=related_recipes, username=username)
@app.route('/wikieats/recipe/<recipeid>/pinrecipe', methods=['POST'])
def pinRecipe(recipeid):
    '''
    Takes a recipeid, pins the recipe to the group which was in the pin form.
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaronadd")
    cur = conn.cursor()
    # Pinning the recipe using the groupid from the form and the recipeid parameter
    cmd = "INSERT INTO pinnedrecipes(groupid, recipeid) VALUES (%s, %s)"
    cur.execute(cmd, (request.form['pin'], recipeid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))
@app.route('/wikieats/groups/<groupid>/<recipeid>/unpinrecipe', methods=['POST'])
def unpinRecipe(recipeid, groupid):
    '''
    Takes the recipeid and groupid and deletes that row from the database.
    '''
    conn = psycopg2.connect("dbname=wikieats user=aarondelete")
    cur = conn.cursor()
    cmd = "DELETE FROM pinnedrecipes WHERE recipeid=%s AND groupid=%s"
    cur.execute(cmd, (recipeid, groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))
@app.route('/wikieats/recipe/<recipeid>/reviewrecipe', methods=['POST'])
def reviewrecipe(recipeid):
    '''
    Putting the review of the recipe of recipeid into the database
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaronadd")
    cur = conn.cursor()
    # Simple enough I mean
    # BTW cgi.escape simply changes all possible XSS characters such as #,>, and & into alphanumeric values
    # This is done to prevent cross site scripting :^(
    cmd = "INSERT INTO reviews (recipeid,reviewtitle,reviewtext,userid,rating) VALUES(%s,%s,%s,%s,%s)"
    cur.execute(cmd, (recipeid, cgi.escape(request.form['Title']), cgi.escape(request.form['review']), session.get('userid'), request.form['rating']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayrecipe', recipeid=recipeid))
@app.route('/wikieats/review/<reviewid>/deletereview', methods=['POST'])
def deletereview(reviewid):
    '''
    Deleting a review, takes the reviewid to delete
    '''
    conn = psycopg2.connect("dbname = wikieats user=aarondelete")
    cur = conn.cursor()
    cmd = "DELETE FROM reviews WHERE reviewid = %s"
    cur.execute(cmd, (reviewid, ))
    conn.commit()
    return redirect(url_for('displayuser', userid=session.get('userid')))
@app.route('/wikieats/user/<userid>', methods=['GET'])
def displayuser(userid):
    '''
    Displays the actual user page. Needs userinfo, recipiesmade, followers, following, groups in, and reviews made
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaron")
    cur = conn.cursor()
    # Gets user information except for password :^)
    cmd = "SELECT userid,username,firstname,lastname from users WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    userinfo = cur.fetchone()
    # Gets all the recipes the user specified made
    cmd = "SELECT recipeid FROM generalrecipes WHERE userid=%s"
    cur.execute(cmd, (userid, ))
    userrecipes = cur.fetchall()
    # Gets all the persons the user is following
    cmd = "SELECT followingid FROM following WHERE followerid = %s"
    cur.execute(cmd, (userid, ))
    following = cur.fetchall()
    # Gets all the people who are following the user
    cmd = "SELECT followerid FROM following WHERE followingid = %s"
    cur.execute(cmd, (userid, ))
    followers = cur.fetchall()
    # Gets all the groups the user is in
    cmd = "SELECT groupid FROM groupmembers WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    groups = cur.fetchall()
    # Gets all the reviews the user made
    cmd = "SELECT reviewid,generalrecipes.recipeid,reviewtitle,reviewtext,rating,title,description,category,categoryname,generalrecipes.userid,username FROM reviews LEFT JOIN generalrecipes ON reviews.recipeid = generalrecipes.recipeid LEFT JOIN recipecategory ON generalrecipes.category = recipecategory.categoryid LEFT JOIN users ON generalrecipes.userid = users.userid WHERE reviews.userid = %s"
    cur.execute(cmd, (userid, ))
    reviews = cur.fetchall()
    return render_template('displayuser.html', userinfo=userinfo, userrecipes=userrecipes, following=following, followers=followers, groups=groups, reviews=reviews)
@app.route('/wikieats/user/<followingid>/follow', methods=['POST'])
def followUser(followingid):
    '''
    Method to follow the user, followingid is the user you want to follow
    '''
    conn = psycopg2.connect('dbname=wikieats user=aaronadd')
    cur = conn.cursor()
    cmd = "INSERT INTO following (followerid, followingid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), followingid))
    conn.commit()
    return redirect(url_for('displayuser', userid=followingid))
@app.route('/wikieats/user/<followingid>/unfollow', methods=['POST'])
def unfollowUser(followingid):
    '''
    Method to unfollow a user, following is the user you want to unfollow.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aarondelete')
    cur = conn.cursor()
    cmd = "DELETE FROM following WHERE followingid = %s AND followerid = %s"
    cur.execute(cmd, (followingid, session.get('userid')))
    conn.commit()
    return redirect(url_for('displayuser', userid=followingid))
@app.route('/wikieats/user/<userid>/manage', methods=['POST'])
def changeaccount(userid):
    '''
    Method to change your account and log the changes in the database.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aaronadd')
    cur = conn.cursor()
    # using cgi.escape to check for XSS
    firstname = cgi.escape(request.form['firstname'])
    lastname = cgi.escape(request.form['lastname'])
    newUsername = cgi.escape(request.form['newusername'])
    # Bcrypt will be explained in login and createaccount
    newPassword = request.form['newpassword']
    oldPassword = request.form['password'].encode('utf-8')
    cmd = "SELECT password, userid FROM users WHERE userid =%s"
    cur.execute(cmd, (userid, ))
    user = cur.fetchone()
    password = user[0].encode('utf-8')
    # If the password is not right, redirect somewhere else
    if not bcrypt.checkpw(oldPassword, password):
        session['error'] = True
        return redirect(url_for('displayuser', userid=userid))
    session['error'] = False
    # The next lines are checking to see if the user actually wants to change and if so changing it
    if firstname:
        cmd = "UPDATE users SET firstname=%s WHERE userid = %s"
        cur.execute(cmd, (firstname, userid))
        conn.commit()
    if lastname:
        cmd = "UPDATE users SET lastname=%s WHERE userid = %s"
        cur.execute(cmd, (lastname, userid))
        conn.commit()
    if newUsername:
        # Checking to see if the username exists
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
        new_password_encode = newPassword.encode('utf-8')
        passwordbcrypt = bcrypt.hashpw(new_password_encode, bcrypt.gensalt()).decode('utf-8')
        cmd = "UPDATE users SET password=%s WHERE userid=%s"
        cur.execute(cmd, (passwordbcrypt, userid))
        conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displayuser', userid=userid))
@app.route('/wikieats/user/<userid>/delete', methods=['POST'])
def deleteaccount(userid):
    '''
    Method to delete account, first deletes all the groups the user leads, then it deletes the rows from groupmembers where the user is in, thne it deletes the user itself.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aarondelete')
    cur = conn.cursor()
    cmd = "SELECT groupid FROM groups WHERE leaderid=%s"
    cur.execute(cmd, (str(userid), ))
    groupsled = cur.fetchall()
    # Deleting all the groups the user leaders in the table groupmembers
    for group in groupsled:
        cmd = "DELETE FROM groupmembers WHERE groupid = %s"
        cur.execute(cmd, (str(group[0]), ))
        conn.commit()
    # Deletes the groups the user leads in the table groups
    cmd = "DELETE FROM groups WHERE leaderid =%s"
    cur.execute(cmd, (userid, ))
    conn.commit()
    # Deleting all the records of the user being in a group
    cmd = "DELETE FROM groupmembers WHERE userid = %s"
    cur.execute(cmd, (userid), )
    conn.commit()
    # Deletes the useritself
    cmd = "DELETE FROM users WHERE userid = %s"
    cur.execute(cmd, (userid, ))
    conn.commit()
    cur.close()
    conn.close()
    session.pop('userid', None)
    return redirect(url_for('loginpage'))
@app.route('/wikieats/login')
def loginpage():
    '''
    Site for the login page
    '''
    if session.get('userid'):
        return redirect(url_for('wikieats'))
    return render_template('login.html')
@app.route('/wikieats/login/login', methods=['POST'])
def login():
    '''
    Login itself, uses bcrypt to hash passwords.
    '''
    if session.get('userid'):
        return redirect(url_for('page_not_found'))
    conn = psycopg2.connect("dbname=wikieats user=aaron")
    cur = conn.cursor()
    # Bcrypt is a very secure password hashing function where you don't even have to store the salt
    # First you have to encode the password into utf-8
    passwordencoded = request.form['password'].encode('utf-8')
    # Getting the actual hashed password from the database
    cmd = 'SELECT password,userid FROM users WHERE username=%s'
    cur.execute(cmd, (request.form['username'], ))
    password = cur.fetchone()
    if password:
        userid = password[1]
        password = password[0].encode('utf-8')
        # bcrypt.checkpw checks to see if the unhashed password is equal to the hashed password
        if bcrypt.checkpw(passwordencoded, password):
            session['userid'] = userid
            session['error'] = False
            return redirect(url_for('wikieats'))
        else:
            # If the password is incorrect than just redirect to another page    
            session['error'] = True
            return redirect(url_for('loginpage'))
    else:
        session['error'] = True
        return redirect(url_for('loginpage'))
@app.route('/wikieats/logout')
def logout():
    '''
    Logout of the wikieats, pops the userid session
    '''
    session.pop('userid', None)
    return redirect(url_for('wikieats'))
@app.route('/wikieats/createaccount')
def createaccountpage():
    '''
    Page for creating an account, does not work if already logged in.
    '''
    if session.get('userid'):
        return redirect(url_for('wikieats'))
    return render_template('createaccount.html')
@app.route('/wikieats/createaccount/create', methods=['POST'])
def createaccount():
    '''
    Actually creating the account!
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaronadd")
    cur = conn.cursor()
    # Does not allow you to view the page if you are already logged in
    cmd = 'SELECT userid FROM users WHERE username = %s'
    cur.execute(cmd, (request.form['username'],))
    # If there is already the username active or the person put the wrong code, errors and redirect
    if cur.fetchone() is not None or request.form['verification'] != conf['wikieatsjoin']:
        return redirect(url_for('createaccountpage'))
        session['error'] = True
    else:
        session['error'] = False
        cmd = "INSERT INTO users (username, firstname, lastname, password) VALUES (%s, %s, %s, %s)"
        # First you encode the password you get into utf-8
        passwordencoded = request.form['password1'].encode('utf-8')
        # Then you salt the password and hash it using bcrypt.hashpw then you decode it from utf-8
        # Don't ask me why you need to encode and then immediately decode, it only works this way
        passwordbcrypt = bcrypt.hashpw(passwordencoded, bcrypt.gensalt()).decode('utf-8')
        cur.execute(cmd, (cgi.escape(request.form['username']),cgi.escape(request.form['fName']), cgi.escape(request.form['lName']), passwordbcrypt))
        conn.commit()
        cmd = "SELECT userid FROM users ORDER BY userid DESC LIMIT 1"
        cur.execute(cmd)
        userid = cur.fetchone()
        session['userid'] = userid[0]
        # Displays newly made user!
        return redirect(url_for('displayuser',userid=userid[0]))
@app.route('/wikieats/creategroup')
def creategrouppage():
    '''
    Page for the form to create the group
    '''
    return render_template('creategroup.html')
@app.route('/wikieats/group/<groupid>', methods=['GET'])
def displaygroup(groupid):
    '''
    Displays the group itself
    '''
    conn = psycopg2.connect("dbname=wikieats user=aaron")
    cur = conn.cursor()
    # Selects all pinned recipes in group
    cmd = "SELECT recipeid FROM pinnedrecipes WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    pinnedrecipes = cur.fetchall()
    # Selects all recipes by group members
    cmd = "SELECT recipeid FROM generalrecipes LEFT JOIN groupmembers ON groupmembers.userid = generalrecipes.userid WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    grouprecipes = cur.fetchall()
    # Selects general group info
    cmd = "SELECT groupid, groupname, groupdescription, leaderid, grouppicture FROM groups WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    groupinfo = cur.fetchone()
    # Selects users in the group
    cmd = "SELECT users.userid, username FROM groupmembers LEFT JOIN users on groupmembers.userid = users.userid WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    groupmembers = cur.fetchall()
    return render_template('displaygroup.html', pinnedrecipes=pinnedrecipes, grouprecipes=grouprecipes, groupinfo=groupinfo, groupmembers=groupmembers)
@app.route('/wikieats/creategroup/create', methods=['POST'])
def creategroup():
    '''
    Creating a group, uploads the information to postgres
    '''
    # Folder where all the grouppics are stored
    app.config['UPLOAD_FOLDER']='static/images/grouppics'
    conn = psycopg2.connect('dbname=wikieats user=aaronadd')
    cur = conn.cursor()
    grouppic = request.files['grouppic']
    grouppicname = secure_filename(grouppic.filename)
    session['right_extension'] = True
    # If the user didn't upload a picture then put the default picture
    if grouppic.filename=="":
        grouppicname = "chef_hat.png"
        extension = '.png'
    else:
        #This is checking to see if the file uploaded is actually an image
        #Seeing if the extensions are right.
        allowed_extensions = ['jpg','jpeg','png',]
        extension = grouppicname.split('.')
        extension = extension[-1]
        if extension not in allowed_extensions:
            session['right_extension'] = False
            return redirect(url_for('creategrouppage'))
        #Naming the group picture by the groupid    
        cmd = "SELECT last_value FROM groups_groupid_seq"
        cur.execute(cmd)
        groupid = cur.fetchone()
        groupid = int(groupid[0])+1
        grouppicname = str(groupid)+'.png'
        grouppic.save(os.path.join(app.config['UPLOAD_FOLDER'], grouppicname))
    cmd = "INSERT INTO groups (groupname, groupdescription, leaderid, grouppicture) VALUES (%s, %s, %s, %s)"
    cur.execute(cmd, (cgi.escape(request.form['groupname']), cgi.escape(request.form['groupdesc']), session.get('userid'), grouppicname))
    conn.commit()
    cmd = "SELECT groupid FROM groups ORDER BY groupid DESC LIMIT 1"
    cur.execute(cmd)
    groupid = cur.fetchone()
    # When the group is created the leader also has the join the group!
    cmd = "INSERT INTO groupmembers (userid, groupid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), groupid[0]))
    conn.commit()
    return redirect(url_for('wikieats', groupid=groupid[0], grouppicname=grouppicname))
@app.route('/wikieats/group/<groupid>/leave', methods=['POST'])
def leavegroup(groupid):
    '''
    User who is logged in leaves the group specified in groupid
    '''
    conn = psycopg2.connect('dbname=wikieats user=aarondelete')
    cur = conn.cursor()
    # Delete row where the user was in the group
    cmd = "DELETE FROM groupmembers WHERE userid = %s AND groupid = %s"
    cur.execute(cmd, (session.get('userid'), groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid=groupid))
@app.route('/wikieats/group/<groupid>/join', methods=['POST'])
def joingroup(groupid):
    '''
    Userid joins the group specified in groupid
    '''
    conn = psycopg2.connect('dbname=wikieats user=aaronadd')
    cur = conn.cursor()
    cmd = "INSERT INTO groupmembers (userid, groupid) VALUES (%s, %s)"
    cur.execute(cmd, (session.get('userid'), groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid=groupid))
@app.route('/wikieats/group/<groupid>/delete')
def deletegroup(groupid):
    '''
    Only the groupleader can delete a group.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aarondelete')
    cur = conn.cursor()
    # Deletes the group from the groups table
    cmd = "DELETE FROM groups WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    conn.commit()
    # Deltes all the group ids from the groupmembers table
    cmd = "DELETE FROM groupmembers WHERE groupid = %s"
    cur.execute(cmd, (groupid, ))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('about'))
@app.route('/wikieats/group/<groupid>/manage', methods=['POST'])
def managegroup(groupid):
    '''
    Sets a new leader when the old one wants to quit.
    '''
    conn = psycopg2.connect('dbname=wikieats user=aaron')
    cur = conn.cursor()
    # Transfer leadership of the group to whoever was selected   
    cmd = "UPDATE groups SET leaderid = %s WHERE groupid = %s"
    cur.execute(cmd, (request.form['transfer'], groupid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('displaygroup', groupid=groupid))
@app.route('/wikieats/search', methods=['GET'])
def search():
    '''
    Displays the search results on the site
    '''
    search = cgi.escape(request.args.get('search'))
    searchparen = '%'+search+'%'
    conn = psycopg2.connect('dbname=wikieats user=aaron')
    cur = conn.cursor()
    # Gets recipes that are like the serach
    cmd = "SELECT recipeid FROM generalrecipes WHERE title LIKE %s"
    cur.execute(cmd, (searchparen, ))
    searchrecipes = cur.fetchall()
    # Gets users who are like the search
    cmd = "SELECT userid FROM users WHERE username LIKE %s"
    cur.execute(cmd, (searchparen, ))
    searchusers = cur.fetchall()
    return render_template('searchrecipe.html', searchrecipes=searchrecipes, searchusers=searchusers, search=search)
@app.errorhandler(404)
def page_not_found(e):
    '''
    404 page not found
    '''
    return render_template('404.html'), 404
