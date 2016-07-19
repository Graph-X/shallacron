#!/usr/bin/python
# This is a python script used to automate the process of verifying, downloading, updated the blacklists 
# for Squid3 and then restarting the service so the new lists can take effect
# ###########################################################################################################
import subprocess
import os, sys
import hashlib
import requests
import tarfile

######
#
# NOTE: YOU WILL WANT TO MAKE SURE THESE VARIABLE ARE CORRECT FOR YOUR SYSTEM.  
# IF YOU STORE YOUR BLACKLISTS IN A DIFFERENT LOCATION YOU NEED TO UPDATE THE DIRECTORY 
# FURTHER DOWN THE SCRIPT AS WELL.
#########################################################################################
url = "http://www.shallalist.de/Downloads/shallalist.tar.gz"
file = "/var/lib/squidguard/shallalist.tar.gz"
squiduser = "13"
squidgrp = "13"

####Begin Functions####

#just makes a simple GET to a webpage
def webget(st=None):
	s = requests.session()
	if st is not None:
		r = s.get(url, st=True)
	else:
		r = s.get(url)
	s.close()
	return r

#retrieved the MD5sum file for the lists and returns the value of it	
def sumfile(url):
	return (webget(url + '.md5').content.split(' ', 1))[0]

#gets the MD5 sum of the old file	
def oldsum(file):
	return hashlib.md5(open(file, 'rb').read()).hexdigest()

#go out and get new lists
def newlist(file):
	r = webget(True)
	try:
		with open(file, 'w') as f:
			f.write(r.raw.read())
		f.close()
	except Exception as e:
		print "The following error occured: " + str(e)
		sys.exit(1)
	return True
	
#verifies integrity of downloaded files as well as preventing duplicate file download if md5sums match on running vs hosted items
def hashcheck(old, new):
	if old == new:
		return False
	else:
		return True

#untars archives
def untar(file):
	tar = tarfile.open(file)
	try:k
		# IF YOU STORE YOUR LIST DATABASE IN A DIFFERENT LOCATION, THIS IS THE OTHER VARIABLE TO CHANGE
		tar.extractall("/var/lib/squidguard/db/")
	except Exception as e:
		print "The following error occured: " + str(e)
		sys.exit(1)
	return True

#changes the file permissions on the blacklists so that the squid proxy again has access to them.
def fileperms():
	path = "/var/lib/squidguard/db/"
	try:
		for root, dirs, files in os.walk(path):
			for dir in dirs:
				os.chown(os.path.join(root, dir), squiduser, squidgrp)
			for file in files:
				os.chown(os.path.join(root, file), squiduser, squidgrp)
	except Exception as e:
		print "The following error occurred: " + str(e)
		sys.exit(1)
	return True

#restarts the squid servicee	
def restart_squid():
	try:
		command = ['service', 'squid3', 'restart']
		subprocess.call(command, shell=False)
	except Exception as e:
		print "The following error occurred: " + str(e)
		sys.exit(1)
	return True
##### END FUNCTIONS ####
	
	
def main(url, file):
	if (hashcheck(oldsum(file), sumfile(url))):
		if newlist(file):
			if untar(file):
				if fileperms:
					if restart_squid:
						print "OK"
						sys.exit(0)
	else:
		print "md5 is the same.  No need to update"
		sys.exit(0)
if __name__ == '__main__':
	main(url, file)