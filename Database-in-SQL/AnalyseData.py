import sqlite3
import operator
from  textblob import TextBlob
import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import apikeys
import oauth2
import json

# twitter application credentials
consumer_key = apikeys.consumer_key
consumer_secret = apikeys.consumer_secret
access_token_key = apikeys.access_token_key
access_token_secret = apikeys.access_token_secret
# credentials end

# Aunthitication to twitter account/server
def twit_req(url, type, post_body, http_headers):
    http_method = type
    cOnsumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    tOken = oauth2.Token(key=access_token_key, secret=access_token_secret)
    cLient = oauth2.Client(cOnsumer, tOken)
    resp, content = cLient.request(url, method=http_method, body=post_body, headers=http_headers)
    return content



# connceting to sqlite3 database to add data to tables
connection = sqlite3.connect("projectTwit.db")
cursor = connection.cursor()
cursor2= connection.cursor()

i=0

# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------

def tagsAssoPerson():
    person= raw_input("Enter twitter handle: ")

    output= "SELECT tag_id from user_tags where user_id='"+ person+"' "

    for row in cursor.execute(output):
        # print row[0]
        getTag="select tag_details from tags where tag_id='"+row[0]+"'"
        tagName=cursor2.execute(getTag)
        print tagName.fetchone()[0]

# ------------------------------------------------------------------------

def similarUsers():
    userHandle= raw_input("Enter Twitter Handle to find: ")

    query= "SELECT tag_id from user_tags where user_id='"+userHandle+"'"
    referenceSet= set()
    for row in cursor.execute(query):
        referenceSet.add(row[0])

    userQuery="SELECT user_id from user where user_id<>'"+userHandle+"'"

    Result=set()

    for row in cursor.execute(userQuery):
        compareSet=set()
        # print row[0]
        compareQuery = "SELECT tag_id from user_tags where user_id='"+row[0]+"'"
        for row2 in cursor2.execute(compareQuery):
            compareSet.add(row2[0])

        resultSet= referenceSet.intersection(compareSet)
        a1=float(len(resultSet))
        a2=float(len(referenceSet))

        try:
            accr= a1/a2
            # print a1
            if accr > 0.75:
                Result.add(row[0])
        except ZeroDivisionError:
            a=0


    for x in Result:
        print x

    if(len(Result)==0):
        print "None Found"

# ------------------------------------------------------------------------


def popularThings():
    print "Popular Things"
    query="select tag_id, count(tag_id) as pm from tweet_tags group by tag_id order by pm desc limit 10;"

    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]

# ------------------------------------------------------------------------

def trendingThings():
    print "Trending Things"
    datesel= raw_input("Enter Date: ")
    query= " select tag_id, count(tag_id) as pm from (select tag_id,date as dt from tweet_tags inner join tweet_details where tweet_tags.tweet_id=tweet_details.tweet_id) where dt='"+datesel+"' group by tag_id order by pm desc limit 10"



    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]

# ------------------------------------------------------------------------

def shouldIFollow():
    print "Enter your UserName:"
    meUsr= raw_input()
    print "Enter UserName to compare"
    usrTwo= raw_input()

    query = "SELECT tag_id from user_tags where user_id='" + meUsr + "'"
    referenceSet = set()
    for row in cursor.execute(query):
        referenceSet.add(row[0])

    query2 = "SELECT tag_id from user_tags where user_id='" + usrTwo + "'"
    compareSet = set()
    for row in cursor.execute(query2):
        compareSet.add(row[0])

    resultSet = referenceSet.intersection(compareSet)
    a1 = float(len(resultSet))
    a2 = float(len(referenceSet))

    try:
        accr = a1 / a2
        if accr > 0.75:
            print "User is "+str(accr*97)+"% matching, you should follow back"
        else:
            print "User is only " + str(accr*97)+"% matching, you should not follow back"

    except ZeroDivisionError:
        print "Users does not Match, Do not Follow"

# ------------------------------------------------------------------------

def tagsToInclude():
    query="select tag_id, sum(retweets) as crt from tweet_details as td inner join tweet_tags as tt where td.tweet_id=tt.tweet_id group by tag_id order by crt desc limit 15;"
    # hashTagsSet = set()
    # for row in cursor.execute(query):
    #     hashTagsSet.add(row[0])

    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]


# ------------------------------------------------------------------------

def bestTimeToTweet():
    query="select time,retweets from tweet_details group by time order by retweets desc;"
    timeDict=dict()
    for row in cursor.execute(query):
        if(timeDict.has_key(int(row[0][0:2]))==False):
            timeDict[int(row[0][0:2])]=int(row[1])
        else:
            temp=timeDict.get(int(row[0][0:2]))
            timeDict[int(row[0][0:2])]=temp+int(row[1])

    sortDict = sorted(timeDict.items(), key=lambda x: x[1], reverse=True)

    print "The best time to tweet is "+str(sortDict[0][0])+":00 to "+str(sortDict[0][0]+1)+":00 hrs"

# ------------------------------------------------------------------------


def urlOrNot():
    queryNo=" select sum(crt), count(crt) from (select urls, retweets as crt from tweet_details as td inner join tweet as t where t.tweet_id= td.tweet_id) where urls='NO_URL' "
    queryYes="select sum(crt), count(crt) from (select urls, retweets as crt from tweet_details as td inner join tweet as t where t.tweet_id= td.tweet_id) where urls<>'NO_URL' "

    avgNo= float()
    avgYes=float()
    for row in cursor.execute(queryNo):
        avgNo=float(row[0])/float(row[1])
    for row in cursor.execute(queryYes):
        avgYes=float(row[0])/float(row[1])

    if(avgNo>avgYes):
        print ("Limit URLs as far as possible")
    else:
        print ("You should use more URLs in Tweets")

# ------------------------------------------------------------------------

def clean_tweet(tweet):
    # Utility function to clean tweet text by removing links, special characters
    # using simple regex statements.
    #
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w+:\ / \ / \S+)", " ", tweet).split())



def peopleSaying():
    userAcc = raw_input("Enter Your User Handle: ")
    query="select tweet_content, retweets from tweet as t inner join tweet_details as td where t.tweet_id=td.tweet_id order by td.retweets desc;"
    resS= set()

    for row in cursor.execute(query):
        if userAcc in row[0].lower():
            resS.add(row[0])

    print ("\nPopular Mentions :\n")
    i=0
    senti=0
    for x in resS:
        if i < 3:
            print "--->"+x
        analysis =TextBlob(clean_tweet(x))
        senti+= analysis.sentiment.polarity
        i+=1
    print("\n\n")
    if  senti  > 0:
        print 'Net Sentiment about '+ userAcc+' is Positive'
    elif senti  == 0:
        print 'Net Sentiment '+ userAcc+' is Neutral'
    else:
        print 'Net Sentiment '+ userAcc+' is Negative'

# -----------------------------------------------------------------------------

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

# remove punctuation, lowercase, stem
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


def postLikeMine():
    referenceTweet = raw_input("Enter Your Tweet to Compare: ")
    query = "select tweet_content, user_id from tweet as t inner join tweet_details as td where t.tweet_id=td.tweet_id order by td.retweets desc;"
    resS = set()

    for row in cursor.execute(query):
        simRating = cosine_sim(clean_tweet(referenceTweet), clean_tweet(row[0]))
        if simRating>0.25:
            resS.add(row)
            # print simRating

    if len(resS)==0:
        print "No Similar Tweets found"

    for row in resS:
        print (row[1]+"-||-"+row[0])
    # print cosine_sim('a little bird', 'i dont know why there is a little bird')

# ------------------------------------------------------------------------------------

def getRetweeters(idss, mine):
    url= "https://api.twitter.com/1.1/statuses/retweeters/ids.json?id="+idss+"&count=100&stringify_ids=true"
    getJson = twit_req(url, "GET", "", "NONE")
    parsedJson = json.loads(getJson)
    relUsers=0
    count=0
    userSet= set()
    for x in parsedJson['ids']:
        urluser="https://api.twitter.com/1.1/followers/ids.json?cursor=-1&user_id="+x+"&count=5000"
        getDetails=twit_req(urluser, "GET", "", "NONE")
        pJson = json.loads(getDetails)
        # print pJson
        for user in pJson['ids']:
            userSet.add(user)
        if count==5:
            break
        count+=1


    print "Potential reach is "+str(len(userSet)+int(mine))


def whatsMyReach():
    tweetId=raw_input("Enter the Tweet id to compare: ")
    query= "select * from tweet_details where tweet_id="+tweetId
    query2= "select * from (select t.user_id, u.followers from tweet as t inner join user as u where tweet_id="+tweetId+")"
    td = cursor2.execute(query)
    tweet=  td.fetchone()
    tt=cursor.execute(query2)
    totFollowers = tt.fetchone()[1]

    if tweet[3]>0:
        getRetweeters(tweet[0], totFollowers)

# -------------------------------------------------------------------

def whatsMyInfluence():
    usrnm = raw_input("Enter the UserName: ")
    query1="select following, followers from user where user_id='"+usrnm+"'"
    ud = cursor2.execute(query1)
    ratiod = ud.fetchone()
    ratio =float(float(ratiod[1])/float(ratiod[0]))

    query2= "select count(*) , avg(retweets), avg(favourate) from (select retweets, favourate, user_id from tweet_details as td inner join tweet as t where td.tweet_id=t.tweet_id) where user_id='"+usrnm+"'"
    td = cursor2.execute(query2)
    rtfavd = td.fetchone()

    # print ratio, rtfavd[0],rtfavd[1],rtfavd[2]
    infPerTweet = ratio*(float((rtfavd[1]+rtfavd[2])/2))

    if infPerTweet<8:
        print "Low Influence"
    if 8<infPerTweet<15:
        print "Moderate Influence"
    if infPerTweet>15:
        print "Highly Influencial "

# ------------------------------------------------------------------------

def viralUserTweets():
    usrnm = raw_input("Enter the UserName: ")
    query2 = "select count(*) , avg(retweets), avg(favourate) from (select retweets, favourate, user_id from tweet_details as td inner join tweet as t where td.tweet_id=t.tweet_id) where user_id='" + usrnm + "'"
    td = cursor2.execute(query2)
    rtfavd = td.fetchone()

    avgdetails=float((rtfavd[1]+rtfavd[2])/2)

    if avgdetails<15:
        print "User is not Viral"
    if 20<avgdetails<100:
        print "User is Moderately Viral"
    if avgdetails>100:
        print "User is Highly Viral "


# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------


while(i!=15):
    print "\n--------------------------------------------------------------------------"
    print "1. Tags Associated with a Person:"
    print "2. What user posts like ______"
    print "3. Things that are popular in our domain"
    print "4. Things that are trending in our domain"
    print "5. Should I follow someone back?"
    print "6. Tags to Include in Tweet"
    print "7. Best time to Tweet"
    print "8. Should you add URLs to Tweets?"
    print "9. Who should I be following"
    print "10. What are People saying about User"
    print "11. Find a similar tweet"
    print "12. Find Reach of Tweet"
    print "13. What is the influence of my post?"
    print "14. How viral are my posts?"
    print "15. Exit"

    try:
        option = int(raw_input('Enter your choice:'))
    except ValueError:
        print "Not a number"

    if(option==1):
        tagsAssoPerson()
    if(option==2):
        similarUsers()
    if(option==3):
        popularThings()
    if(option==4):
        trendingThings()
    if(option==5):
        shouldIFollow()
    if(option==6):
        tagsToInclude()
    if(option==7):
        bestTimeToTweet()
    if(option==8):
        urlOrNot()
    if (option == 9):
        similarUsers()
    if (option == 10):
        peopleSaying()
    if(option==11):
        postLikeMine()
    if(option==12):
        whatsMyReach()
    if (option == 13):
        whatsMyInfluence()
    if (option == 14):
        viralUserTweets()
    if(option==15):
        i=15
        print "Exiting Program"



# ------------------------------------------------------------------------# ------------------------------------------------------------------------
# ------------------------------------------------------------------------# ------------------------------------------------------------------------











