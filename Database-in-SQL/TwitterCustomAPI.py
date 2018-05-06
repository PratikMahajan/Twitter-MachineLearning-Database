# from twitter import *
# import requests
import oauth2
import json
#import urllib
#import time
import sqlite3
from sets import Set
import apikeys


# twitter application credentials
consumer_key = apikeys.consumer_key
consumer_secret = apikeys.consumer_secret
access_token_key = apikeys.access_token_key
access_token_secret = apikeys.access_token_secret
# credentials end


#list of hashtags that we will be scarping from twitter
hashtagsTwitter = Set(['datascience', 'ArtificialIntelligence', 'Machinelearning', 'BigData', 'deepLearning', 'neuralnetworks', 'Automation'])


# connceting to sqlite3 database to add data to tables
connection = sqlite3.connect("projectTwit.db")
cursor = connection.cursor()
cur2=connection.cursor()

# from twitter api imported above
# refer https://github.com/sixohsix/twitter
# def twitter_api():
#     t = Twitter(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
#     return t


# function oauth
#  normally we dont require post_body and http_headers for twitter soo while passing,
#  default http_header to be passes is NONE and post_body is a blank string
def twit_req(url, type, post_body, http_headers):
    http_method = type
    cOnsumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    tOken = oauth2.Token(key=access_token_key, secret=access_token_secret)
    cLient = oauth2.Client(cOnsumer, tOken)
    resp, content = cLient.request(url, method=http_method, body=post_body, headers=http_headers)
    return content


# the above function is used to connect to twitter and use its core api
# as mentioned on https://dev.twitter.com/rest/reference/
# we can use this to connect and use post/get or use the
# twitter python library to get information
# in the above function we use oauth to connect to twitter
# for more information see: https://dev.twitter.com/oauth/overview/single-user

# when we send and get response through twit_req() function
# it returns a json file. we've to parse this file and then use it
# to parse the json object that we get we import json and use the function
# json.loads()

# given below example of getting the twitter timeline
# url="https://api.twitter.com/1.1/statuses/home_timeline.json?count=5"
# r=twit_req(url,"GET","","NONE")
# parsedJson=json.loads(r)
# for i in range(len(parsedJson)):
#    print parsedJson[i]["text"]

# as we're sending all the requests through url. we've to encode string into the url
# for encoding string we use urllib library and encode it with function quote_plus()
# example as show below
# url="https://api.twitter.com/1.1/statuses/update.json"
# status="post Check #python"
# uri=[]
# uri.append(url)
# uri.append("?status=")
# uri.append(urllib.quote_plus(status))
# uri=''.join(uri)
# print uri
# r=twit_req(uri,"POST","","NONE")


def GET_HomeT_NO(number):
    homeurl = "https://api.twitter.com/1.1/statuses/home_timeline.json?count="
    homeurl += number
    getJson = twit_req(homeurl, "GET", "", "NONE")
    parsedJson = json.loads(getJson)

    for i in range(len(parsedJson)):

        addToUser(parsedJson[i])
        addTweet(parsedJson[i])


    connection.commit()
    connection.close()



def Search_tweets(list,count):
    searchUrl="https://api.twitter.com/1.1/search/tweets.json?"
    countPart="count="+count+"&"
    for x in list:
        finalUrl= searchUrl+countPart+"q="+x
        print finalUrl
        getJson = twit_req(finalUrl, "GET", "", "NONE")
        parsedJson = json.loads(getJson)

        for i in range(len(parsedJson["statuses"])):
            addToUser(parsedJson["statuses"][i])
            connection.commit()
            addTweet(parsedJson["statuses"][i])
            connection.commit()
            addTweetTags(parsedJson["statuses"][i])

    removeTagDuplicates()
    removeSynonymsAndMispellings()
    connection.commit()
    connection.close()



# example to get the sample search json from twitter
# below function is only for studying the search json from twitter
# for reference refer twitter search json on twitter api documentation
def searchJson():
    searchUrl = "https://api.twitter.com/1.1/search/tweets.json?count=10&q=datascience"
    getJson = twit_req(searchUrl, "GET", "", "NONE")
    parsedJson = json.loads(getJson)
    eg=parsedJson["statuses"]
    for i in range(len(eg)):
        print(eg[i]["text"]+"||")
        print("\n")
        for k in range(len( eg[i]["entities"]["hashtags"])):
            print str(eg[i]["entities"]["hashtags"][k]["text"]) # print all the hashtags that are tagged in the tweet






# demo stream api
# url= "https://userstream.twitter.com/1.1/user.json"
# r=twit_req(url,"GET","","NONE")
# while True:
#        print json.dumps(r)
#
#        time.sleep(1)





#adding user to database
# sqlite> .schema user
# CREATE TABLE user(user_id varchar(25) not null primary key , user_name varchar(50), followers int, following int, tweet_count int);
def addToUser(parsedJson):
    try:
        cursor.execute("INSERT INTO user VALUES ('" + '@' + parsedJson["user"]["screen_name"] + "','" +
                       parsedJson["user"]["name"].replace("'", " ") + "', " + str(parsedJson["user"]["followers_count"]) + "," +
                       str(parsedJson["user"]["friends_count"]) + "," + str(parsedJson["user"]["statuses_count"]) + ")")
        print "userAdded"
    except sqlite3.IntegrityError:
        # if we are trying to add same user to database again this except block occurs.
        # here we will update the user if that particular user's followers and following and tweet count is changed
        cursor.execute("UPDATE user SET followers="+str(parsedJson["user"]["followers_count"])+" , following= "+str(parsedJson["user"]["friends_count"])+
                       ", tweet_count="+ str(parsedJson["user"]["statuses_count"])+"  WHERE user_id='+"+'@'+parsedJson["user"]["screen_name"]+"'")
        print "UsedUpdated"


#adding tweet and tweet details to database

# sqlite> .schema tweet_details
# CREATE TABLE tweet_details(tweet_id varchar(25) not null primary key, date varchar(10),time varchar(8), favourate int, retweets int );
# sqlite> .schema tweet
# CREATE TABLE tweet(tweet_id varchar(25) not null primary key, user_id varchar(25),tweet_content varchar(300), urls varchar(100) );
def addTweet(parsedJson):
    try:
        dateForm = cleanDate(parsedJson["created_at"])
        try:
            cursor.execute(
                "INSERT INTO tweet VALUES('" + str(parsedJson["id"]) + "' , '" + '@' + parsedJson["user"]["screen_name"] + "','" +
                parsedJson["text"].replace("'", " ") + "','" +parsedJson["entities"]["urls"][0]["expanded_url"] + "')")

            cursor.execute(
                "INSERT INTO tweet_details VALUES ('" + str(parsedJson["id"]) + "','" + dateForm[0] + "','" +
                dateForm[1] + "', " + str(parsedJson["favorite_count"]) + "," + str(parsedJson["retweet_count"]) + ")")
            print "TweetAdded"

        except IndexError:
            # if the tweet contains no url this except codeblock is executed with cleaned url
            cursor.execute(
                "INSERT INTO tweet VALUES('" + str(parsedJson["id"]) + "' , '" + '@' + parsedJson["user"]["screen_name"] + "','" +
                parsedJson["text"].replace("'", " ") + "','NO_URL')")

            cursor.execute(
                "INSERT INTO tweet_details VALUES ('" + str(parsedJson["id"]) + "','" + dateForm[0] + "','" +
                dateForm[1] + "', " + str(parsedJson["favorite_count"]) + "," + str(parsedJson["retweet_count"]) + ")")
            print "TweetAddedException"
    except sqlite3.IntegrityError:
         #if we are trying to add same tweet again to the database, sqlintegrity error occurs. this block is to handle that exception
         print "addtweetException"






# tables in the database are as follows:
# sqlite> .schema tags
# CREATE TABLE tags(tag_id integer not null primary key autoincrement, tag_details varchar(50) );
# sqlite> .schema user_tags
# CREATE TABLE user_tags(tag_no integer not null primary key autoincrement, user_id varchar(25), tag_id varchar(25));
# sqlite> .schema tweet_tags
# CREATE TABLE tweet_tags(tag_no integer not null primary key autoincrement, tweet_id varchar(25), tag_id varchar(25));
# sqlite> .schema tags
# CREATE TABLE tags(tag_id integer not null primary key autoincrement, tag_details varchar(50) );
# sqlite>

def addTweetTags(parsedJson):
    try:
        for k in range(len(parsedJson["entities"]["hashtags"])):
             # print str(parsedJson["entities"]["hashtags"][k]["text"])
             hashadd= parsedJson["entities"]["hashtags"][k]["text"]
             cursor.execute(
                 "INSERT INTO tags(tag_details) values('" + hashadd.lower()+ "')"
             )
             # print "TagAddedDatabase"+"INSERT INTO tags(tag_details) values('" + parsedJson["entities"]["hashtags"][k]["text"] + "')"
        connection.commit()
    except sqlite3.IntegrityError:
        print "TagAddedException"

    try:
        for k in range(len(parsedJson["entities"]["hashtags"])):

            temp = cursor.execute(
                 "select tag_id from tags WHERE tag_details='" + parsedJson["entities"]["hashtags"][k]["text"].lower() + "'"
            )
            abc1=str(parsedJson["id"])
            tagid=str(temp.fetchone()[0])
            print tagid
            cursor.execute(
                 "INSERT INTO tweet_tags(tweet_id,tag_id) values('" + abc1 + "','" +tagid + "')"
             )
            userid='@' + parsedJson["user"]["screen_name"]
            connection.commit()
            # print ("INSERT INTO user_tags(user_id,tag_id) values('" + userid + "','" + tagid + "')")
            cursor.execute(
                 "INSERT INTO user_tags(user_id,tag_id) values('" + userid + "','" + tagid + "')"
             )
            connection.commit()
            print "TweetAndUserTagsAdded"
    except TypeError:
        print "!!!!!!!!!!!!!!!!"



def removeTagDuplicates():
    cursor.execute("  delete from user_tags where tag_no NOT IN (select min(tag_no) from user_tags group by user_id,tag_id) ")
    connection.commit()
    cursor.execute(" delete from tweet_tags where tag_no NOT IN (select min(tag_no) from tweet_tags group by tweet_id,tag_id) ")
    connection.commit()


def removeSynonymsAndMispellings():
    res= cursor.execute(" SELECT orig_tag_id,syn_tag_id FROM synonym ")
    for row in res:
        cur2.execute('UPDATE user_tags Set tag_id=? where tag_id=?',(row[0], row[1], ))
        cur2.execute('UPDATE tweet_tags Set tag_id=? where tag_id=?', (row[0], row[1],))
    connection.commit()
    res = cursor.execute(" SELECT orig_tag_id,misp_tag_id FROM mispelling ")
    for row in res:
        cur2.execute('UPDATE user_tags SET tag_id=? WHERE tag_id=?', (row[0], row[1],))
        cur2.execute('UPDATE tweet_tags SET tag_id=? WHERE tag_id=?', (row[0], row[1],))
    connection.commit()


# function to clean date to proper format instead of twitter default format
def cleanDate(fullDate):
    splitDate = fullDate.split(" ");
    formatDate = str(splitDate[5]) + "-" + str(getMonth(splitDate[1])) + "-" + str(splitDate[2])
    return [formatDate, splitDate[3]]

# Part of cleanDate function to get month number instead of string
def getMonth(month):
    if (month == "Jan"):
        return "01"
    if (month == "Feb"):
        return "02"
    if (month == "Mar"):
        return "03"
    if (month == "Apr"):
        return "04"
    if (month == "May"):
        return "05"
    if (month == "Jun"):
        return "06"
    if (month == "Jul"):
        return "07"
    if (month == "Aug"):
        return "08"
    if (month == "Sept"):
        return "09"
    if (month == "Oct"):
        return "10"
    if (month == "Nov"):
        return "11"
    if (month == "Dec"):
        return "12"


# to run the script from here
#GET_HomeT_NO("5")

# Search_tweets(Set(["neuralnetworks","MachineLearning","BigData"]),"199")
Search_tweets(hashtagsTwitter,"199")

# searchJson()