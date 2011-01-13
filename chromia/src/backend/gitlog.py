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
import os

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

os.environ["GIT_DIR"] = "/Volumes/Data1/environment/chromia.org/chromia.repo/chromia/.git/"
os.system("git remote update")

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
	
#show_data()      
db.close() 
#print os.environ["GIT_DIR"][:-5]
 
if have_changes==1:
	os.system("build_new.py")
	
	
