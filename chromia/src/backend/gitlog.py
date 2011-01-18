#!/usr/bin/env python

#
# Copyright (C) 2011 Kirill Gordeev <kirill.gordeev@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import MySQLdb
import os, time

import hashlib
import subprocess
import re
import sys

from rfc822 import parsedate
from time import mktime
from datetime import datetime

cmt=[]
autor=None
commit_id=None
files=None
insertions=None
deletions=None

capture_commit_text=0
have_changes  = None

chromia_ver = "0.1" #Future get from README soruce file

# Config section

chromia_src_dir = "/Volumes/Data1/environment/chromia.org/chromia.repo/chromia/"  
chromia_pub_dir = "/home/kg/builds/pub/"

db_host         ="localhost"
db_user         ="root"
db_pass         =""
db_name         ="chromia"

# Main program section

os.environ["GIT_DIR"] = chromia_src_dir +".git/"
os.system("git pull")

db = MySQLdb.connect(db_host,db_user,db_pass, db_name )


def md5(fileName, excludeLine="", includeLine=""):
    """Compute md5 hash of the specified file"""
    m = hashlib.md5()
    try:
        fd = open(fileName,"rb")
    except IOError:
        print "Unable to open the file in readmode:", filename
        return
    eachLine = fd.readline()
    while eachLine:
        if excludeLine and eachLine.startswith(excludeLine):
            continue
        m.update(eachLine)
        eachLine = fd.readline()
    m.update(includeLine)
    fd.close()
    return m.hexdigest()
		   

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)		   


def add_commit_info():
	
	if cmt is not None:
		commit_msg = cmt.__str__().replace(",","").replace("'","").replace("[","\n\r").replace("]","").replace("-","\n\r -").strip()
		cursor = db.cursor()
		sql = "INSERT INTO cms_gitlog(commit_id, autor, commit_date, cmt, files, insertions, deletions) \
		       VALUES ('%s', '%s', '%s', '%s' ,'%d', '%d', '%d')" % \
		       (commit_id, autor, d, commit_msg, files, insertions, deletions )
		try:
		   cursor.execute(sql)		    
  		   db.commit()  
   		   return 1 		
		except:
		   db.rollback()

git = subprocess.Popen(["git", "log", "--shortstat", "--reverse"], stdout=subprocess.PIPE)
out, err = git.communicate()
total_files, total_insertions, total_deletions = 0, 0, 0

for line in out.split('\n'):
    if not line: continue
    
    if line.startswith('commit '):
    	commit_id=line[7:].strip()
    	
    if line.startswith('Author:'):
    	a = line[7:].split("<")
    	autor = a[0].strip()
        
    if line.startswith('Date:'):
    	d=datetime(*parsedate(line[5:])[:7])
    	t=mktime(parsedate(line[5:]))
    	capture_commit_text=1
    	continue
    
    data = re.findall(' (\d+) files changed, (\d+) insertions\(\+\), (\d+) deletions\(-\)', line)
    if len(data)>0: # final commit
    	capture_commit_text = 0
    	files, insertions, deletions = ( int(x) for x in data[0] )
    	if add_commit_info()==1:
    		have_changes = 1
    	cmt=[]
    	
    if len(line.strip())>1 and capture_commit_text==1:
    	cmt.append(line.strip())
    		    
 	
# Build new version if have new comiits 
if have_changes==1:
	cursor = db.cursor()
	cursor.execute ("SELECT MAX(ID) FROM cms_chromiabuild")
	last_build = cursor.fetchone ()[0]
	
	
	if (last_build==None):
		last_build = 1
	else:
		last_build +=1		
		
	os.system("./build_deb.sh chromia-%s.%s %s" %(chromia_ver, last_build, chromia_src_dir) )
	out_file = "chromia_%s.%d-1_i386.deb" % (chromia_ver,last_build)
	
	if (os.path.isfile(chromia_pub_dir+out_file)):
		f_build_date = modification_date(chromia_pub_dir+out_file)
		f_md5        = md5(chromia_pub_dir+out_file)
		f_size 		 = os.path.getsize(chromia_pub_dir+out_file)
		
		cursor = db.cursor()
		sql = "INSERT INTO cms_chromiabuild(version_id, md5sum, build_date, file_size,  package_file) \
		       VALUES ('%s', '%s', '%s', '%d','%s' )" % \
		       ( "chromia_%s.%d"%(chromia_ver,last_build), f_md5, f_build_date, f_size, out_file)
		try:
		   cursor.execute(sql)		    
   		   db.commit()  		
		except:
		   db.rollback()
	
db.close()	
