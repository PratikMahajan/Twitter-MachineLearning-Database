#!/usr/bin/python
from pymongo import MongoClient
import sqlite3
import json

#connecting to mongodb
client = MongoClient('localhost', 27017)
db=client.proj

# connceting to sqlite3 database to add data to tables
connection = sqlite3.connect("projectTwit.db")
cursor = connection.cursor()
cursor2 = connection.cursor()
cursor3 = connection.cursor()


# Transferring Data From SQL database to non Relational Database 



#
# Tables are
# User---Tweet---Tweet_details---Tags---User_tags---Tweet_tags
# ...
# -----user(user_id varchar(25) not null primary key , user_name varchar(50), followers int, following int, tweet_count int);
# -----tweet_details(tweet_id varchar(25) not null primary key, date varchar(10),time varchar(8), favourate int, retweets int )
# -----tweet(tweet_id varchar(25) not null primary key, user_id varchar(25),tweet_content varchar(300), urls varchar(100) )
# -----tags(tag_id integer not null primary key autoincrement, tag_details varchar(50) )
# -----user_tags(tag_no integer not null primary key autoincrement, user_id varchar(25), tag_id varchar(25))
# -----tweet_tags(tag_no integer not null primary key autoincrement, tweet_id varchar(25), tag_id varchar(25))
# ...
#
# We need not insert tags_id into the database.
# instead we will direct insert all the tags for a tweet or a user directly in colledtion.
#
# Collection User will have all the data of that user and tags directly in a column
#
# Collection Tweets will have data from tweet table and tweet_details and directly hashtags inserted, instead if ids.
#
# Collection user:
# {
# 	"user_id":,
# 	"user_name":,
# 	"followers":,
# 	"following":,
# 	"tweet_count":,
# 	"hashtags":[ ]
# }
#
# Collection tweet:
# {
# 	"tweet_id":,
# 	"user_id":,
# 	"tweet_contents":,
# 	"urls":,
# 	"date":,
# 	"time":,
# 	"favourites":,
# 	"retweets":,
# 	"hashtags":[ ]
# }


def getAndPopulateUsers():

    mainQuery="Select * from user"

    for row in cursor.execute(mainQuery):

        output= "SELECT tag_id from user_tags where user_id='"+ row[0]+"' "
        list = []
        for row2 in cursor2.execute(output):
            try:
                getTag="select tag_details from tags where tag_id='"+row2[0]+"'"
                tagName=cursor3.execute(getTag)
                list.append(tagName.fetchone()[0])
            except Exception as e:
                print "none"
        res= ('{ "user_id": "%s" , "user_name": "%s", "followers": %d, "following": %d, "tweet_count": %d, "hashtags": %s  }' %(row[0],row[1],row[2],row[3],row[4], str(list).replace("'","\"").replace("u","").replace("\\","") ) )
        print (res)
        break
        db.user.insert_one(json.loads(res))



def getandPopulateTweets():

    mainQuery=" Select * from tweet inner join tweet_details where tweet.tweet_id=tweet_details.tweet_id"

    for row in cursor.execute(mainQuery):
        output = "SELECT tag_id from tweet_tags where tweet_id='" + row[0] + "' "
        list = []
        for row2 in cursor2.execute(output):
            try:
                getTag = "select tag_details from tags where tag_id='" + row2[0] + "'"
                tagName = cursor3.execute(getTag)
                list.append(tagName.fetchone()[0])
            except Exception as e:
                print "none"
        res= ('{ "tweet_id": "%s", "user_id": "%s", "tweet_contents": "%s", "urls": "%s", "date": "%s", "time": "%s", "favourites": %d, "retweets": %d, "hashtags": %s }'  %(row[0], row[1], row[2].replace("\n"," ").replace("\"",""), row[3], row[5], row[6], row[7], row[8], str(list).replace("'","\"").replace("u\"","\"").replace("\\","")   ))
        print (res)
        db.tweet.insert_one(json.loads(res))


# getandPopulateTweets()
print("\n\n\n")
getAndPopulateUsers()