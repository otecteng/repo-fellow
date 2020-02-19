import os
import mysql.connector
import logging

class RepoMySQL:
    def init_db(self, root_password, host = "localhost", fellow_db = "repo_fellow", fellow_user = "repo", fellow_password = "fellow"):
        logging.info("create database on {}".format(host))
        logging.info("new database: user={} database={}".format(fellow_user,fellow_db))

        db_script = "{}/resources/init.sql".format(os.path.dirname(__file__))
        
        cnx = mysql.connector.connect(user="root", password = root_password, host = host)
        try:
            with open(db_script,"r",encoding="utf-8") as f:
                cursor = cnx.cursor()
                results = cursor.execute(f.read(),multi = True)
                try:
                    for result in results:
                        logging.info(result)
                        pass
                except Exception as e:
                    pass 
                cursor.close()               
        except Exception as ex:
            logging.error(ex)
        cnx.close()
