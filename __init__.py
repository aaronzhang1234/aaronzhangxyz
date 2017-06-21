from .aaronzhangxyz import app
import psycopg2
from flask import redirect, url_for

def printrecipe(recipeid):
  conn = psycopg2.connect("dbname=wikieats user=postgres")
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
  conn = psycopg2.connect("dbname=wikieats user=postgres")
  cur = conn.cursor()
  cmd = "SELECT * FROM pinnedrecipes WHERE groupid = %s and recipeid=%s"
  cur.execute(cmd, (groupid, recipeid))
  pinned_recipe = cur.fetchone()
  if pinned_recipe is None:
      return False
  else:
      return True

def printstep(step):
  return '<div class="row"><div class="col-md-12 col-md-offset-1"><h2>Step'+ str(step[0])+'</h2></div><div class="col-md-3 col-md-offset-1"><img src="../../static/images/recipeimages/'+step[2]+'" alt="'+step[2]+'" class="img-responsive"/></div><div class="col-md-5"><p>'+step[1]+'</p></div></div>'

def printreview(review):
  conn = psycopg2.connect('dbname=wikieats user=postgres')
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
  conn = psycopg2.connect('dbname=wikieats user=postgres')
  cur = conn.cursor()
  cmd = "SELECT * FROM groups WHERE groupid = %s AND leaderid = %s"
  cur.execute(cmd, (groupid, userid))
  groupLeader = cur.fetchone()
  if groupLeader is None:
      return False;
  else:
      return True;

def inGroup(groupid, userid):
  conn = psycopg2.connect('dbname=wikieats user=postgres')
  cur = conn.cursor()
  cmd = "SELECT * FROM groupmembers WHERE groupid = %s AND userid=%s"
  cur.execute(cmd, (groupid, userid))
  groupMember = cur.fetchone()
  if groupMember is None:
      return False;
  else:
      return True;

def printgroup(groupid):
  conn = psycopg2.connect('dbname = wikieats user=postgres')
  cur = conn.cursor()
  cmd = "SELECT groupid, groupname, groupdescription, grouppicture FROM groups WHERE groupid = %s"
  cur.execute(cmd, (groupid, ))
  group = cur.fetchone()
  return '<div class = "col-md-12 panel"><div class="col-md-4"><img src="../../static/images/grouppics/'+ str(group[3]) +'" alt="'+str(group[1])+'" class="img-thumbnail"/> </div><div class="col-md-8"><h3><a href="'+ url_for('displaygroup',groupid=groupid)+'">'+str(group[1])+'</a></h3><p>'+str(group[2])+'</p></div></div><hr/>'

def printuser(user):
  conn = psycopg2.connect('dbname=wikieats user=postgres')
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
  conn = psycopg2.connect('dbname=wikieats user=postgres')
  cur = conn.cursor()
  cmd = "SELECT * FROM following WHERE followingid = %s AND followerid=%s"
  cur.execute(cmd, (followingid, followerid))
  following = cur.fetchone()
  if following is None:
      return False
  else:
      return True

def printcarousel(recipeid, active = ""):
  conn = psycopg2.connect('dbname=wikieats user=postgres')
  cur = conn.cursor()
  cmd = "SELECT title, description, imagename FROM generalrecipes WHERE recipeid = %s"
  cur.execute(cmd, (recipeid, ))
  recipe = cur.fetchone()
  return '<div class="item'+active+'"><img style="display:block;margin:auto;width:90%" src="../static/images/recipeimages/'+recipe[2]+'" alt="'+recipe[0]+'" width="500" height="345"><div class="carousel-caption"><h3>'+recipe[0]+'</h3><p>'+recipe[1]+'</p></div></div>'

app.jinja_env.globals.update(printrecipe=printrecipe, printstep=printstep, printreview=printreview,isPinned=isPinned, isLeader=isLeader, inGroup=inGroup, printuser=printuser, isFollowing=isFollowing, printgroup=printgroup, printcarousel=printcarousel)
