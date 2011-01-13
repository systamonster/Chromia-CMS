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

from rfc822 import parsedate
from time import mktime
from datetime import datetime
from os import popen
from sys import argv,stderr,stdout
from subprocess import call

cmt=[]
autor=None
h=[]
capture_commit_text=0
commit_id=None
have_changes  = None

chromia_ver = "0.1" #Future get from README soruce file
chromia_src_dir = "/home/kg/builds/chromia/chromia/"
chromia_pub_dir = "/home/kg/builds/pub/"

os.environ["GIT_DIR"] = chromia_src_dir +".git/"
os.system("git pull")

db = MySQLdb.connect("localhost","root","","chromia" )

 
def show_data():
	if cmt is not None:
		commit_msg = cmt.__str__().replace(",","").replace("'","").replace("[","\n\r").replace("]","\n\r").strip()
		pstr="%s %s %s %s"%(autor,commit_id,d,commit_msg)
		#print pstr
		h.append((autor,commit_id,d,commit_msg))
		cursor = db.cursor()
		sql = "INSERT INTO cms_gitlog(commit_id, autor, commit_date, cmt) \
		       VALUES ('%s', '%s', '%s', '%s' )" % \
		       (commit_id, autor, d, commit_msg)
		try:
		   cursor.execute(sql)		    
   		   db.commit()  
   		   return 1 		
		except:
		   db.rollback()

		   
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
		   
		   
			   
for x in popen('git log --reverse -p'):

	if x.startswith('Date:'):	
		d=datetime(*parsedate(x[5:])[:7])
		t=mktime(parsedate(x[5:]))		
		capture_commit_text=1
		continue
	
	if x.startswith('commit '):
		commit_id=x[7:].strip()	

	if x.startswith('Author:'):
 	 	autor=x[7:].strip()
 	
	if x.startswith('diff --') and capture_commit_text==1 :
                capture_commit_text=0
                if show_data() ==1:
                	have_changes=1
                cmt=[]
		
        if len(x.strip())>1 and capture_commit_text==1:
                cmt.append(x[:-1].strip())
	
 
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
		f_build_date = time.ctime(os.path.getmtime(chromia_pub_dir+out_file))
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
