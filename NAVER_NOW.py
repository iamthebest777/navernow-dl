#!/usr/bin/env python3

import requests 
import datetime
import os
import argparse
import time

parser=argparse.ArgumentParser()
parser.add_argument('--channel', required=False)
args = parser.parse_args()

def decrypt_url(ct_b64):
	
	global DECRYPTED
	
	from Cryptodome import Random
	from Cryptodome.Cipher import AES
	import base64
	from hashlib import md5
	
	BLOCK_SIZE = 16
	
	def pad(data):
		length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
		return data + (chr(length)*length).encode()
	
	def unpad(data):
		return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]
	
	def bytes_to_key(data, salt, output=48):
		assert len(salt) == 8, len(salt)
		data += salt
		key = md5(data).digest()
		final_key = key
		while len(final_key) < output:
			key = md5(key + data).digest()
			final_key += key
		return final_key[:output]
	
	def encrypt(message, passphrase):
		salt = Random.new().read(8)
		key_iv = bytes_to_key(passphrase, salt, 32+16)
		key = key_iv[:32]
		iv = key_iv[32:]
		aes = AES.new(key, AES.MODE_CBC, iv)
		return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))
	
	def decrypt(encrypted, passphrase):
		encrypted = base64.b64decode(encrypted)
		assert encrypted[0:8] == b"Salted__"
		salt = encrypted[8:16]
		key_iv = bytes_to_key(passphrase, salt, 32+16)
		key = key_iv[:32]
		iv = key_iv[32:]
		aes = AES.new(key, AES.MODE_CBC, iv)
		return unpad(aes.decrypt(encrypted[16:]))
	
	KEY = '!@7now$%1api)6*'.encode()
	DECRYPTED = decrypt(ct_b64, KEY).decode('utf-8')
	return DECRYPTED

def send_email(msg,subject,isfrom,isto):
	import smtplib
	from email.mime.text import MIMEText
	
	ACCID = "s1531178@student.mcckc.edu"
	APPPW = "nbayfksuzojllocx"
	
	if isfrom == "ME":
		isfrom = ACCID
	else:
		pass
	if isto == "ME":
		isto = ACCID
	else:
		pass
	
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(ACCID, APPPW)
	
	message = MIMEText(msg)
	message['Subject'] = subject
	s.sendmail(isfrom,isto,message.as_string())
	print("Successfully Sent Email!")
	s.quit()

#CHANNEL_CODE = 913
CHANNEL_CODE = args.channel
DATE = datetime.datetime.now().strftime("%y%m%d")
LIVE_URL = "https://now.naver.com/api/nnow/v2/stream/%s/livestatus/"%CHANNEL_CODE
INFO_URL = "https://now.naver.com/api/nnow/v2/stream/%s/content/"%CHANNEL_CODE
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
		VIDEO_STREAM_URL = live_data['streamUrl'].replace('playlist.m3u8', 'chunklist_1080p.m3u8')
		VIDEO_STREAM_URL = decrypt_url(VIDEO_STREAM_URL)
		TITLE = info_data['title']['text'].replace("\r\n"," ").replace("w/","with").replace("W/","with").replace("/","").replace('"',"'")
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
		print (now.strftime("%m/%d/%Y %H:%M:%S")+" : 라이브 시간이 아닙니다", end="\r", flush=True)
		time.sleep(1)
		
		

print("\nStarting Download...\n")

cmd='streamlink -o "%s" "%s" best'%(FILE_NAME,VIDEO_STREAM_URL)
time.sleep(2)
os.system(cmd)
print("Download Completed")

print("Moving File to Google Drive..")

mv_cmd = 'rclone move "/home/ubuntu/%s" "OMG_DATA:03 VIDEO DATA/TEMP/AGIT_TEMP" -P -v'%FILE_NAME
os.system(mv_cmd)

print("Process Done!")
LOG = '''
FILENAME: %s
STATUS: Successfully Downloaded and Uploaded it to Google Drive!

@ Proudly Done by HYPE'''%FILE_NAME
send_email(LOG,"[NAVER NOW. DOWNLOADER] TASK REPORT", "ME", "ME")
