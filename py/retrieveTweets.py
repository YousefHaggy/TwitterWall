from flask_cors import CORS 
from flask import Flask, jsonify, render_template, request
from bs4 import BeautifulSoup
import urllib3
import time
app=Flask(__name__)
CORS(app)
http=urllib3.PoolManager()
@app.route('/_return_tweets')
def _return_tweets():
	tweetList=[]
	baseUrl=u'https://twitter.com/hashtag/'
	httprequest=http.request("GET",baseUrl+request.args.get('hashtag')+"?f=tweets&vertical=news")

	soup=BeautifulSoup(httprequest.data,'lxml')
	mainTweetDiv=soup.findAll('div',class_="tweet")
	ids=[tweet['data-item-id'] for tweet in mainTweetDiv]
	tweetText=[tweet.find('p', class_='tweet-text').text for tweet in mainTweetDiv]
	usernames=[tweet.find('strong',class_='fullname').text for tweet in mainTweetDiv]
	imageLinks=[""]*len(mainTweetDiv)
	for i in range(len(mainTweetDiv)):
		if mainTweetDiv[i].find('div',class_='AdaptiveMedia-photoContainer') is not None:
			imageLinks[i]=mainTweetDiv[i].find('div',class_='AdaptiveMedia-photoContainer')['data-image-url'] 
	profileImages=[tweet.find('img',class_="avatar")['src'] for tweet in mainTweetDiv]
	for i in range(len(mainTweetDiv)):
		tweetList.append(Tweet(tweetText[i],usernames[i],imageLinks[i],profileImages[i],ids[i]).serialize())
	return jsonify(result=tweetList);

class Tweet():
 	def __init__(self,text,username,imageLink,profileImage,id):
 		self.text=text;
 		self.username=username;
 		self.imageLink=imageLink;
 		self.profileImage=profileImage
 		self.id=id
 	def serialize(self):
 		return{
 		'text': self.text,
 		'username':self.username,
 		'imageLink': self.imageLink,
 		'profilephoto':self.profileImage,
 		'id':self.id
 		}
if __name__=="__main__":
	app.run()