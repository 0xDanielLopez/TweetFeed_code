# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Usage:
# python3 tweetfeed.py
#
# Install:
# pip3 install tweepy iocextract
#
# @0xDanielLopez 2022

import tweepy
import iocextract		# From https://github.com/InQuest/python-iocextract
from tags import *		# Tags being searched
from whitelist import *	# Whitelist URLs, domains, etc
from secrets import *	# Twitter API keys (get yours at https://developer.twitter.com/apps)
from datetime import datetime, timedelta
import os
import glob
import csv

#Colours
RED = '\033[91m'
ENDC = '\033[0m'
GREEN = '\033[1;32m'
WHITE = '\033[1m'
BOLD = '\033[01m'
BLUE = '\033[94m'
ORANGE = '\033[38;5;202m'

# Parameters
max_tweets = 100

# Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
whoami=api.verify_credentials().screen_name

# Query 1 (search tags) "#phishing OR #scam ... -filter:retweets -filter:replies"
query1 = " OR ".join(tags)
query1 = query1 + " -filter:retweets -filter:replies" #query1 = tags + " -filter:retweets -filter:replies"

# Query 2 (search in TweetFeed list https://twitter.com/i/lists/1423693426437001224)
query2 = "list:1423693426437001224"

# Search Tweets
searched_tweets1 = [status for status in tweepy.Cursor(api.search_tweets, q=query1,result_type="recent",tweet_mode='extended').items(max_tweets)]
searched_tweets2 = [status for status in tweepy.Cursor(api.search_tweets, q=query2,result_type="recent",tweet_mode='extended').items(max_tweets)]

searched_tweets = searched_tweets1 + searched_tweets2

# Control Rate Limit (see https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits)
data = api.rate_limit_status()	#Rate limit
remaining=data["resources"]["search"]["/search/tweets"]["remaining"] 	# Remaining rate limit

# IOCs already seen
seen_urls=[]
seen_ips=[]
seen_sha256=[]
seen_md5=[]

outputs=glob.glob("output/*.csv")

for output in outputs:
	with open(output) as iocs_file:
		iocs_reader = csv.reader(iocs_file, delimiter=',')
		for row in iocs_reader:

			if row[2] == "url":
				seen_urls.append(row[3])
			elif row[2] == "ip":
				seen_ips.append(row[3])
			elif row[2] == "sha256":
				seen_sha256.append(row[3])
			elif row[2] == "md5":
				seen_md5.append(row[3])

# IOCs new
new_urls=[]
new_ips=[]
new_sha256=[]
new_md5=[]

# Get IOCS
for tweet in reversed(searched_tweets):

	# Check if the user is in whitelist
	tweet_user=tweet.user.screen_name

	if tweet_user in whitelist_users:
		continue

	# Get Tweet's text. If it's a retweet get the retweeted text
	if hasattr(tweet, 'retweeted_status'):
		text=tweet.retweeted_status.full_text
	else:
		text=tweet.full_text

	# To add more IOCs check https://inquest.readthedocs.io/projects/iocextract/en/latest/#more-details
	urls=iocextract.extract_urls(text, refang=True)
	ips=iocextract.extract_ips(text, refang=True)
	sha256s=iocextract.extract_sha256_hashes(text)
	md5s=iocextract.extract_md5_hashes(text)

	# Get URLs
	for url in urls:
		if url not in seen_urls and not url.startswith("https://t.co") and url not in whitelist_urls:

			# Info about the Tweet
			if hasattr(tweet, 'retweeted_status'):
				tweet_date=tweet.retweeted_status.created_at
				tweet_user=tweet.retweeted_status.user.screen_name
				tweet_id=tweet.retweeted_status.id
			else:
				tweet_date=tweet.created_at	
				tweet_user=tweet.user.screen_name
				tweet_id=tweet.id

			f_out="output/" + tweet_date.strftime('%Y%m%d.csv')
			tweet_date=tweet_date.strftime('%Y-%m-%d %H:%M:%S')

			ioc_type="url"
			ioc_value= url

			tweet_tags=""
			n_tags=0
			for tag in tags:
				if tag.lower() in tweet.full_text.lower():
					if n_tags==0:
						tweet_tags=tag
					else:
						tweet_tags=tweet_tags + " " + tag
					n_tags += 1

			tweet_url="https://twitter.com/{}/status/{}".format(tweet_user,tweet_id)

			row=[tweet_date,tweet_user,ioc_type,ioc_value,tweet_tags,tweet_url]			

			with open(f_out, mode='a') as iocs_file:
				iocs_writer = csv.writer(iocs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				iocs_writer.writerow(row)

			seen_urls.append(url)
			new_urls.append(url)

	# Get IPs
	for ip in ips:
		if ip not in seen_ips and ip not in whitelist_ips:

			# Info about the Tweet
			if hasattr(tweet, 'retweeted_status'):
				tweet_date=tweet.retweeted_status.created_at
				tweet_user=tweet.retweeted_status.user.screen_name
				tweet_id=tweet.retweeted_status.id
			else:
				tweet_date=tweet.created_at	
				tweet_user=tweet.user.screen_name
				tweet_id=tweet.id

			f_out="output/" + tweet_date.strftime('%Y%m%d.csv')
			tweet_date=tweet_date.strftime('%Y-%m-%d %H:%M:%S')

			ioc_type="ip"
			ioc_value= ip

			tweet_tags=""
			n_tags=0
			for tag in tags:
				if tag.lower() in tweet.full_text.lower():
					if n_tags==0:
						tweet_tags=tag
					else:
						tweet_tags=tweet_tags + " " + tag
					n_tags += 1

			tweet_url="https://twitter.com/{}/status/{}".format(tweet_user,tweet_id)

			row=[tweet_date,tweet_user,ioc_type,ioc_value,tweet_tags,tweet_url]

			with open(f_out, mode='a') as iocs_file:
				iocs_writer = csv.writer(iocs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				iocs_writer.writerow(row)

			seen_ips.append(ip)
			new_ips.append(ip)

	# Get SHA256s
	for sha256 in sha256s:
		if sha256 not in seen_sha256:

			# Info about the Tweet
			if hasattr(tweet, 'retweeted_status'):
				tweet_date=tweet.retweeted_status.created_at
				tweet_user=tweet.retweeted_status.user.screen_name
				tweet_id=tweet.retweeted_status.id
			else:
				tweet_date=tweet.created_at	
				tweet_user=tweet.user.screen_name
				tweet_id=tweet.id

			f_out="output/" + tweet_date.strftime('%Y%m%d.csv')
			tweet_date=tweet_date.strftime('%Y-%m-%d %H:%M:%S')

			ioc_type="sha256"
			ioc_value= sha256

			tweet_tags=""
			n_tags=0
			for tag in tags:
				if tag.lower() in tweet.full_text.lower():
					if n_tags==0:
						tweet_tags=tag
					else:
						tweet_tags=tweet_tags + " " + tag
					n_tags += 1

			tweet_url="https://twitter.com/{}/status/{}".format(tweet_user,tweet_id)

			row=[tweet_date,tweet_user,ioc_type,ioc_value,tweet_tags,tweet_url]

			with open(f_out, mode='a') as iocs_file:
				iocs_writer = csv.writer(iocs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				iocs_writer.writerow(row)

			seen_sha256.append(sha256)
			new_sha256.append(sha256)

	# Get MD5s
	for md5 in md5s:
		if md5 not in seen_md5:

			# Info about the Tweet
			if hasattr(tweet, 'retweeted_status'):
				tweet_date=tweet.retweeted_status.created_at
				tweet_user=tweet.retweeted_status.user.screen_name
				tweet_id=tweet.retweeted_status.id
			else:
				tweet_date=tweet.created_at	
				tweet_user=tweet.user.screen_name
				tweet_id=tweet.id

			f_out="output/" + tweet_date.strftime('%Y%m%d.csv')
			tweet_date=tweet_date.strftime('%Y-%m-%d %H:%M:%S')

			ioc_type="md5"
			ioc_value= md5

			tweet_tags=""
			n_tags=0
			for tag in tags:
				if tag.lower() in tweet.full_text.lower():
					if n_tags==0:
						tweet_tags=tag
					else:
						tweet_tags=tweet_tags + " " + tag
					n_tags += 1

			tweet_url="https://twitter.com/{}/status/{}".format(tweet_user,tweet_id)

			row=[tweet_date,tweet_user,ioc_type,ioc_value,tweet_tags,tweet_url]

			with open(f_out, mode='a') as iocs_file:
				iocs_writer = csv.writer(iocs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				iocs_writer.writerow(row)

			seen_md5.append(md5)
			new_md5.append(md5)

# Print info in terminal
print(40*"=")
print(ORANGE + "Rate remaining: " + ENDC + str(remaining) + " (@" + whoami + ")")
print(40*"=")
print(BLUE + "[+] Query 1: " + ENDC + query1)
print(40*"=")
print(BLUE + "[+] Query 2: " + ENDC + query2)
print(40*"=")
print(BLUE + "[+] Number of tweets analyzed:" + ENDC + " {} tweets ({} tweets per query)".format(len(searched_tweets),max_tweets))
print(40*"=")
print(GREEN + "[+] IOCs added:" + ENDC)
print("\t- URLs: " + str(len(new_urls)))
print("\t- IPs: " + str(len(new_ips)))
print("\t- SHA256: " + str(len(new_sha256)))
print("\t- MD5: " + str(len(new_md5)))
print(40*"=")