import re
import matplotlib.pyplot as plt
import psycopg2
from wordcloud import WordCloud
from imgurpython import ImgurClient
from datetime import date, timedelta
import json
import numpy as np
'''
This program is to make the graph and show the top users
'''
def imgur_authenticate():
    '''
    Used to authenticate and create the imgur object
    '''
    conf = json.load(open ('config.json', 'r'))
    client_id = conf["imgur_id"]
    client_secret = conf["imgur_secret"]
    return ImgurClient(client_id, client_secret)
def makegraph(): 
    '''
    This Function creates a graph of the top 10 twitters users from the day before and plots them to compare their usage.
    '''
    plt.figure(1)
    conn = psycopg2.connect("dbname=tweets user=postgres")
    cur = conn.cursor()
# Getting the top 10 most active users and putting them in the toptweeters variable
    cur.execute("SELECT twitter_id FROM tweets WHERE DATE=TIMESTAMP 'yesterday' GROUP BY twitter_id ORDER BY COUNT(*) DESC LIMIT 10;")
    toptweeters = cur.fetchall()
    tweetDictionary = {}
    # Looping through all the toptweeters
    for user in toptweeters:
        userPlot = [0]
        tweets = 0
        # Getting # of tweets made per hour going by intervals of 59 minutes and 59 seconds
        for hour in range(0, 24):
            # Time has to be formatted in HH:MM:SS so this is just adding an extra 0 to the beginning of the time if hour is less than 10
            timestart = str(hour)+":00:00" if hour >= 10 else "0"+str(hour)+":00:00"
            timeend = str(hour)+":59:59" if hour >= 10 else "0"+str(hour)+":59:59"
            # Gets # of tweets made each hour and adding it to the variable tweets which is the total amount.
            # Afterward, it appends the running total to an array which will be used for the graph.
            cmd = "SELECT COUNT(*) FROM tweets WHERE twitter_id =%s AND time >%s AND time<%s AND DATE=TIMESTAMP 'yesterday';"
            cur.execute(cmd, (user, timestart, timeend))
            num = cur.fetchone()
            tweets = tweets+int(num[0])
            userPlot.append(tweets)
        #The loop is adding all the # of tweets to the array
        # When it is done, it adds a new item to the dictionary using the twitter id as the key
        tweetDictionary[user] = userPlot
    # This is just sorting the dictionary by the max number of tweets made.
    keys = sorted(tweetDictionary, key=lambda x: (tweetDictionary[x][24], x), reverse=True)
    for key in keys:
        # This query is only used for gathering the handle of the user for easier viewing of the legend
        cmd = "SELECT handle FROM twitter_ids WHERE twitter_id =%s"
        cur.execute(cmd, (key))
        handle = cur.fetchone()
        #plt plot is the matplotlib command that adds a newline onto a graph
        #The parameters are the values of the Y axis, in this case the number of the tweets
        #Label is the handle of the user
        plt.plot(tweetDictionary[key], label=handle[0])
    # Creating the legend and saving the figure to something named lol.png
    plt.legend(loc='best')
    # Style changes
    plt.xlabel("Time of Day (24 Hour Clock)")
    plt.ylabel("# of Tweets made (Cumulatively)")
    plt.xticks(range(0, 25), fontsize=5)
    plt.gca().xaxis.grid(True)
    plt.xlim(xmin=0.0,xmax=24)
    plt.ylim(ymin=0.0)
    plt.savefig('static/images/twitter_analytics/twitter_analytics_for'+yesterday.strftime("%Y")+'-'+yesterday.strftime("%m")+'-'+yesterday.strftime("%d")+'.png')
    #image = client.upload_from_path("twitter_analytics.png")
    #return image['id']
def wordcloud():
    '''
    Creates a wordcloud from the tweets finding keywords for the day
    '''
    plt.figure(2)
    conn = psycopg2.connect("dbname=tweets user=postgres")
    cur = conn.cursor()
    cmd = "SELECT tweet FROM tweets WHERE DATE = TIMESTAMP 'yesterday'"
    cur.execute(cmd)
    tweets2 = []
    tweets = cur.fetchall()
    # Since fetchall returns an array of arrays, the for loop is to seperate the values out and put them in one array.
    for tweet in tweets:
        tweets2.append(tweet[0])
    # Creating a string from the array of tweets
    tweetstring = ' '.join(tweets2)
    # Getting rid of all URL's and RT's from the string
    tweetstring = re.sub(r"https\S+", "", tweetstring)
    tweetstring = tweetstring.replace(" RT ", " ")
    tweetstring = re.sub(r"\bsay\S+", "", tweetstring )
    tweetstring = tweetstring.replace(" new "," ")
    #Creating wordcloud from the string
    wordcloud = WordCloud().generate(tweetstring)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('static/images/twitter_analytics/twitter_wordcloud_for'+yesterday.strftime("%Y")+'-'+yesterday.strftime("%m")+'-'+yesterday.strftime("%d")+'.png')
    #image = client.upload_from_path("twitter_wordcloud.png")
    #return image['id']
    # Saving the image in an imgur page.
def createAlbum():
    image_ids = []
    # getting the image ids from the two images made
    image_ids.append(makegraph())
    image_ids.append(wordcloud())
    fields = {}
    fields['title'] = "Twitter Analytics for "+ time.strftime("%x")
    fields['description'] = "Graph and Wordcloud for twitter analytics"
    print(fields)
    x = client.create_album(fields) 
    image = client.album_add_images(x['id'], image_ids)  #Making Album
    print(image)

if __name__ == '__main__':
   yesterday=date.today()-timedelta(1)
   #client = imgur_authenticate() 
   makegraph()
   wordcloud()
   #createAlbum()
