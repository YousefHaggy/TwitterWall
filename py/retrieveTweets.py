from flask_cors import CORS 
from flask import Flask, jsonify, render_template, request
from bs4 import BeautifulSoup
import urllib3
import time
import youtube_dl
app=Flask(__name__)
CORS(app)
http=urllib3.PoolManager()
ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
cachedTweets=[]
@app.route('/_return_tweets')
def _return_tweets():
	tweetList=[]
	global cachedTweets
	gifs=request.args.get('gifs')
	print(gifs)
	if len(cachedTweets)>30:
		cachedTweets=cachedTweets[19:]
	baseUrl=u'https://twitter.com/hashtag/'
	httprequest=http.request("GET",baseUrl+request.args.get('hashtag')+"?f=tweets&vertical=news")

	soup=BeautifulSoup(httprequest.data,'lxml')
	mainTweetDiv=soup.findAll('div',class_="tweet")
	ids=[tweet['data-item-id'] for tweet in mainTweetDiv]
	tweetText=[tweet.find('p', class_='tweet-text').text for tweet in mainTweetDiv]
	usernames=[tweet.find('strong',class_='fullname').text for tweet in mainTweetDiv]
	imageLinks=[""]*len(mainTweetDiv)
	videoLinks=[""]*len(mainTweetDiv)
	for i in range(len(mainTweetDiv)):
		if mainTweetDiv[i].find('div',class_='AdaptiveMedia-photoContainer') is not None:
			imageLinks[i]=mainTweetDiv[i].find('div',class_='AdaptiveMedia-photoContainer')['data-image-url']
		if mainTweetDiv[i].find('div',class_="PlayableMedia-player") is not None:
			for tweet in cachedTweets:
				if tweet.id == ids[i]:
					videoLinks[i]=tweet.videoLink[i]
			if videoLinks[i]=="" and gifs=="yes":
				videoUrl="https://twitter.com/i/videos/tweet/"+ids[i]
				with ydl:
					result=ydl.extract_info(videoUrl,download=False)
				if 'entries' in result:
					videoLinks[i]=result['entries'][0]	
				videoLinks[i]=result['url']
				cachedTweets.append(CachedTweet(ids[i],videoLinks))
	profileImages=[tweet.find('img',class_="avatar")['src'] for tweet in mainTweetDiv]

	for i in range(len(mainTweetDiv)):
		tweetList.append(Tweet(tweetText[i],usernames[i],imageLinks[i],profileImages[i],ids[i],videoLinks[i]).serialize())
	return jsonify(result=tweetList);

class Tweet():
 	def __init__(self,text,username,imageLink,profileImage,id,videoLink):
 		self.text=text;
 		self.username=username;
 		self.imageLink=imageLink;
 		self.profileImage=profileImage
 		self.id=id
 		self.videoLink=videoLink
 	def serialize(self):
 		return{
 		'text': self.text,
 		'username':self.username,
 		'imageLink': self.imageLink,
 		'profilephoto':self.profileImage,
 		'id':self.id,
 		'videoLink':self.videoLink
 		}
class CachedTweet():
 	def __init__(self,id,videoLink):
 		self.id=id
 		self.videoLink=videoLink
if __name__=="__main__":
	app.run()