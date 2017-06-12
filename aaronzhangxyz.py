'''
My website
'''
import pusher
import psycopg2
import os.path
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import json
app = Flask(__name__)
app.config.from_object(__name__)

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
    conn = psycopg2.connect("dbname=morsemessenger user=postgres")
    cur = conn.cursor()
    # if user is in a channel or event already, it takes them to the message send screen
    if session.get('channel') and session.get('event'):
        cmd = 'SELECT message FROM messages WHERE channel=%s AND event=%s ORDER by id'
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
    conn = psycopg2.connect("dbname=morsemessenger user=postgres")
    cur = conn.cursor()
    # Adds the message into the database on the channel and event
    cmd = "insert into messages(channel, event,message) values (%s, %s, %s)"
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

@app.route('/projects')
def projects():
    '''
    For projects page.
    '''
    return render_template('projects.html')

@app.route('/twitteranalytics', methods=['GET'])
def twitteranalytics():
    '''
    analyzing tweets
    '''
    opt_param = request.args.get("twitterdate")
    determine=""
    if opt_param is None:
        determine = "No Get"
    else:
        location_graph = "static/images/twitter_analytics/graphs/"+opt_param+".png"
        location_cloud = "static/images/twitter_analytics/wordclouds/"+opt_param+".png"
        my_graph_exists = os.path.exists(location_graph)
        my_cloud_exists = os.path.exists(location_cloud)
        if my_graph_exists and my_cloud_exists:
            determine = [location_graph, location_cloud]
        else:
            determine = "DNE"
    return render_template('twitteranalytics.html', determine=determine)

@app.route('/twitteranalytics/choosedate', methods=['POST'])
def choosedate():
    return redirect(url_for('twitteranalytics'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
