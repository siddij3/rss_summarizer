from libs.db_rss_feeds import RSSDatabase
from libs.sql_manager import get_db_creds
from libs.sql_manager import SQLManager

import mysql.connector
from mysql.connector import errorcode

creds = {  "host":"localhost",
          "user":"junaid",
          "password":"junaid",
          "database":"rss_feeds",
          "auth_plugin":'mysql_native_password'}
    
def make_tables():
  TABLES = {}
  TABLES['employees'] = (
    "CREATE TABLE `employees` ("
    "  `emp_no` int(11) NOT NULL AUTO_INCREMENT,"
    "  `first_name` varchar(14) NOT NULL,"
    "  PRIMARY KEY (`emp_no`)"
    ") ENGINE=InnoDB")
  
  TABLES['departments'] = (
    "CREATE TABLE `departments` ("
    "  `dept_no` char(4) NOT NULL,"
    "  `dept_name` varchar(40) NOT NULL,"
    "  PRIMARY KEY (`dept_no`), UNIQUE KEY `dept_name` (`dept_name`)"
    ") ENGINE=InnoDB")
  return True
  


class TestDBRSSFeedsMethods: 

  def setup_method(self): 

    creds = get_db_creds()
    self.host=creds["host"]
    self.user=creds["user"]
    self.password=creds["password"]
    self.database=creds["database"]
    self.auth_plugin=creds["auth_plugin"]

    self.sql_manager = SQLManager(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        auth_plugin=self.auth_plugin,
                        mydb=None)


  def test_connect_to_db(self): 
    print(self.sql_manager.__dict__)
    assert self.sql_manager is not None 

