#!/usr/bin/env python3

import requests 
import datetime
import os
import argparse
import time

parser=argparse.ArgumentParser()
parser.add_argument('--channel', required=True)
args = parser.parse_args()

CHANNEL_CODE = args.channel

DATE = datetime.datetime.now().strftime("%y%m%d")
LIVE_URL = "https://now.naver.com/api/nnow/v1/stream/%s/livestatus/"%CHANNEL_CODE
INFO_URL = "https://now.naver.com/api/nnow/v1/stream/%s/content/"%CHANNEL_CODE
print("")
		
while True:
	live_response = requests.get(LIVE_URL)
	info_response = requests.get(INFO_URL)
	live_data = live_response.json()
	live_data = live_data['status']
	info_data = info_response.json()
	info_data = info_data["contentList"][0]
	STATUS = live_data['status']
		
	if STATUS == "ONAIR":
		
		VIDEO_STREAM_URL = live_data['videoStreamUrl']
		TITLE = info_data['title']['text'].replace("\r\n"," ")
		SHOW_NAME = info_data["home"]["title"]["text"]
		HOST_NAME = info_data["home"]["title"]["subtext"]
		num = info_data["count"].replace("회","")
		
		if len(num) == 1:
			EP_NUM="E0%s"%num
		else:
			EP_NUM="E%s"%num
			
		FILE_NAME = "%s NAVER NOW. %s %s %s 1080p.WEB-DL.H264.AAC.ts"%(DATE,SHOW_NAME,EP_NUM,TITLE)
		print("\nSTATUS: %s\nSHOW NAME: %s\nTITLE: %s (%s)\nFILENAME: %s"%(STATUS,SHOW_NAME,TITLE,EP_NUM,FILE_NAME))
		print("STREAM URL: %s"%VIDEO_STREAM_URL)
		
		break
	
	else:
		now = datetime.datetime.now() + datetime.timedelta(seconds=1)
		print (now.strftime("%m/%d/%Y %H:%M:%S")+" : 라이브 시간이 아닙니다. 라이브 시작시간까지 대기중..", end="\r", flush=True)
		time.sleep(1)
		
print("\nStarting Download...\n")

time.sleep(1)
cmd='streamlink -o "%s" "%s" best'%(FILE_NAME,VIDEO_STREAM_URL)
os.system(cmd)
print("Download Completed")
