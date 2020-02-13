import mysql.connector
import logging

class RepoMySQL:
    def init_db(self, root_password, host = "localhost", db_name = "repo_fellow", db_user = "repo", db_password = "fellow"):
        logging.info("create database on {}".format(host))
        logging.info("new database: user={} database={}".format(db_user,db_name))
        cnx = mysql.connector.connect(user="root", password = root_password, host = host)
        with open("init.sql","r",encoding="utf-8") as f:
            cursor = cnx.cursor()
            results = cursor.execute(f.read(),multi=True)
            for cur in results:
                if cur.with_rows:
                    logging.info('result:', cur.fetchall())
        cnx.close()
