import sqlite3
import operator


# connceting to sqlite3 database to add data to tables
connection = sqlite3.connect("projectTwit.db")
cursor = connection.cursor()
cursor2= connection.cursor()

i=0

def tagsAssoPerson():
    person= raw_input("Enter twitter handle: ")

    output= "SELECT tag_id from user_tags where user_id='"+ person+"' "

    for row in cursor.execute(output):
        # print row[0]
        getTag="select tag_details from tags where tag_id='"+row[0]+"'"
        tagName=cursor2.execute(getTag)
        print tagName.fetchone()[0]


def similarUsers():
    print "Similar Users:"
    userHandle= raw_input("Enter Twitter Handle to find similar users: ")

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




def popularThings():
    print "Popular Things"
    query="select tag_id, count(tag_id) as pm from tweet_tags group by tag_id order by pm desc limit 10;"

    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]


def trendingThings():
    print "Trending Things"
    datesel= raw_input("Enter Date: ")
    query= " select tag_id, count(tag_id) as pm from (select tag_id,date as dt from tweet_tags inner join tweet_details where tweet_tags.tweet_id=tweet_details.tweet_id) where dt='"+datesel+"' group by tag_id order by pm desc limit 10"



    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]


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



def tagsToInclude():
    query="select tag_id, sum(retweets) as crt from tweet_details as td inner join tweet_tags as tt where td.tweet_id=tt.tweet_id group by tag_id order by crt desc limit 15;"
    # hashTagsSet = set()
    # for row in cursor.execute(query):
    #     hashTagsSet.add(row[0])

    for row in cursor.execute(query):
        getTag = "select tag_details from tags where tag_id='" + row[0] + "'"
        tagName = cursor2.execute(getTag)
        print tagName.fetchone()[0]


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
    if(option==15):
        i=15
        print "Exiting Program"
