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
import os, re, hashlib, subprocess, sys

from rfc822 import parsedate
from time import mktime
from datetime import datetime

# Config section
chromia_src_dir = "/Volumes/Data1/environment/chromia.org/chromia.repo/chromia/"  
chromia_pub_dir = "/home/kg/builds/pub/"

db_host         ="localhost"
db_user         ="root"
db_pass         =""
db_name         ="chromia"


class GitLog:
              
    def __init__(self, db, src_dir, pub_dir):
        
        self.db = db
        self.src_dir = src_dir
        self.pub_dir = pub_dir
        
        self.commit_msg = []
        self.commit_autor = None
        self.commit_id = None
        self.commit_date = None
        self.commit_files = None 
        self.commit_inserts = None
        self.commit_dels = None
        
        
        self.added_commits = 0
    
    def main(self):
        
        log = self.get_git_log()
        have_changes = self.parse_git_log(log)        
        if have_changes == 1:
            new_version_id = self.get_build_version()
            print "Added new commits %d " % self.added_commits 
            print "Start new build with version %d " % new_version_id
            self.build_new_vesrion(new_version_id)
        else:
            print "No changes found in git tree"  
        

    def get_git_log(self):
        
        os.environ["GIT_DIR"] = self.src_dir +".git/"
        os.system("git pull")
        git = subprocess.Popen(["git", "log", "--shortstat", "--reverse"], stdout=subprocess.PIPE)
        out, err = git.communicate()
        return out
    
    
    def parse_git_log(self, git_log):
        
        capture_commit_text = 0 
        have_changes = 0
        
        for line in git_log.split('\n'):
            if not line: continue
        
            if line.startswith('commit '):
                self.commit_id=line[7:].strip()               
        
            if line.startswith('Author:'):
                a = line[7:].split("<")
                self.commit_autor = a[0].strip()
            
            if line.startswith('Date:'):
                self.commit_date=datetime(*parsedate(line[5:])[:7])
                #t=mktime(parsedate(line[5:]))
                capture_commit_text=1
                continue
                   
            final_line = re.findall(' (\d+) files changed, (\d+) insertions\(\+\), (\d+) deletions\(-\)', line)
            if len(final_line)>0: # final commit
                capture_commit_text = 0
                self.commit_files, self.commit_inserts, self.commit_dels = ( int(x) for x in final_line[0] )
            
            
                if self.set_commit_info() == 1:
                    have_changes = 1
                    self.commit_msg=[]
                
                
            if len(line.strip())>1 and capture_commit_text==1:
                self.commit_msg.append(line.strip())
        
        return have_changes           
         
    
    def set_commit_info(self):
              
        if self.commit_msg is None:
            return 
        
        commit_msg = self.commit_msg.__str__().replace(",","").replace("'","")
        commit_msg = commit_msg.replace("[","\n\r").replace("]","").replace("-","\n\r -").strip()
        
        cursor = db.cursor()
        sql = "INSERT INTO \
                cms_gitlog (commit_id, autor, commit_date, cmt, files, insertions, deletions) \
                VALUES ('%s', '%s', '%s', '%s' ,'%d', '%d', '%d')" % \
               (self.commit_id, self.commit_autor, self.commit_date, commit_msg, 
                self.commit_files, self.commit_inserts, self.commit_dels )
                      
        try:
           cursor.execute(sql)
           db.commit()
           self.added_commits =+1
           
           return 1         
        except MySQLdb.IntegrityError:
           db.rollback()
           return 0
        
        except MySQLdb.ProgrammingError as error:
            print "Error to insert log: %s" % error

           

    def get_build_version(self):
        
        cursor = db.cursor()
        cursor.execute ("SELECT MAX(ID) FROM cms_chromiabuild")
        last_build = cursor.fetchone()[0]
        
        if (last_build==None):
            last_build = 1
        else:
            last_build +=1
            
        return last_build         
               


    def build_new_vesrion(self, new_version_id):                
       
        chromia_ver = "0.1"  #Future get from README soruce file
        tar_file    = "chromia-%s.%s.tar.gz" %(chromia_ver, new_version_id)
               
        # Build .deb file            
        os.system("./build_deb.sh chromia-%s.%s %s" %(chromia_ver, new_version_id, self.src_dir) )
        out_file = "chromia_%s.%d-1_i386.deb" % (chromia_ver, new_version_id)
        
        full_file_name = self.pub_dir+out_file
        if (os.path.isfile(full_file_name)):
            f_build_date = self.get_modification_date(full_file_name)
            f_md5        = self.get_md5sum(full_file_name)
            f_size          = os.path.getsize(full_file_name)
            
            cursor = db.cursor()
            sql = "INSERT INTO cms_chromiabuild(version_id, md5sum, build_date, file_size,  package_file, tar_file) \
                   VALUES ('%s', '%s', '%s', '%d','%s','%s' )" % \
                   ( "chromia_%s.%d"%(chromia_ver, new_version_id), f_md5, f_build_date, f_size, out_file, tar_file)
            try:
               cursor.execute(sql)
               db.commit()          
            except:
               db.rollback()
    

    def get_md5sum(self, file_name, excludeLine="", includeLine=""):
        
        """Compute md5 hash of the specified file"""
        m = hashlib.md5()
        try:
            fd = open(file_name,"rb")
        except IOError:
            print "Unable to open the file in readmode:", file_name
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
    		   
    
    def get_modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)		   



# Start program

db = None
try:
    db = MySQLdb.connect(db_host,db_user,db_pass, db_name )
except:
    print "Unable to connect to database server" 
program = GitLog(db,chromia_src_dir, chromia_pub_dir)
program.main()
db.close()
    
