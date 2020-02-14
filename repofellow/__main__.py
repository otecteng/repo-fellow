"""repo crawler via command-line.

Usage:
    repo-fellow project <command> [<args>]
    repo-fellow user <command> [<args>]
    repo-fellow commit <command> [<args>]
    repo-fellow event <command> [<args>]
    repo-fellow db <command> [<args>]
    repo-fellow pr <command> [<args>]
    repo-fellow site <command> [<args>]
    repo-fellow group <command> [<args>]

Options: 
    -h,--help        

Example:
    repo-fellow db init root:xxx@localhost
    repo-fellow site add https://user:password@site?name&type
    repo-fellow projects remote owner
    repo-fellow projects list
    repo-fellow projects import site_id
    repo-fellow commit update *
    repo-fellow commit update project
"""
import os
import sys
import re
import json
import time
import datetime
import logging
from docopt import docopt
from repofellow.crawler import Crawler
from repofellow.injector import Injector,Commit,Site
from repofellow.parser import Parser
from repofellow.repo_mysql import RepoMySQL

def get_arg(key,default_value = None, args = None):
    if key in os.environ:
        return os.environ[key]
    if args and key in args:
        return args[key]
    return default_value

def main():
    logging.basicConfig(filename = "log/fellow.log", level = logging.INFO, format = "%(asctime)s %(message)s", filemode='a')
    logger = logging.getLogger()    
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    arguments = docopt(__doc__, version = 'Repo Fellow')
    command = arguments["<command>"]

    db_user, db_password, db = get_arg("FELLOW_USER","repo"), get_arg("FELLOW_PASSWORD","fellow"), get_arg("FELLOW_DB","repo_fellow")

    injector = Injector(db_user = db_user, db_password = db_password,database = db)
    site = Site()
    site.server_type,site.url,site.token = get_arg("GIT_SERVER"), get_arg("GIT_SITE"), get_arg("GIT_TOKEN")
    if arguments["project"]:
        if command == "list":
            for i in injector.get_projects():
                logging.info(i)
        if command == "import":
            site = injector.get_obj(Site,arguments["<args>"])
            injector = Injector(db_user = db_user, db_password = db_password,database = db)
            data = Crawler(site,injector).import_projects()
            logging.info("total imported projects {}".format(len(data)))
        if command == "remote":
            site = injector.get_obj(Site,arguments["<args>"])
            commits = Crawler.create_client(site).getAllProjectCommitsCount("china")
            for i in commits:
                if i["ref"]:
                    logging.info("{}:{}".format(i["name"],i["ref"]["target"]["history"]["totalCount"]))
                else:
                    logging.error("{} has none history record".format(i["name"]))
        if command == "update":
            site = injector.get_obj(Site,arguments["<args>"])
            injector = Injector(db_user = db_user, db_password = db_password,database = db)
            data = Crawler(site,injector).update_projects()


    if arguments["user"]:
        if command == "import":
            site = injector.get_obj(Site,arguments["<args>"])
            data = Crawler(site,injector).import_users()
            logging.info("total imported users {}".format(len(data)))

    if arguments["pr"]:
        if command == "import":
            project = arguments["<args>"]
            data = Crawler.create_client(site).get_pull_requests(project)
            injector.insert_data(Parser.parse_pulls(data))
            logging.info("total imported pulls {}".format(len(data)))

    if arguments["commit"]:
        if command == "update":
            site_id, projects = arguments["<args>"].split(":")
            site = injector.get_obj(Site,site_id)
            logging.info("importing from {} of projects {} ".format(site.name,projects))
            injector = Injector(db_user = db_user, db_password = db_password,database = db)
            Crawler(site,injector).import_commits(projects)
                
    if arguments["db"]:
        if command == "init":
            if arguments["<args>"]:
                db_user, db_password, db_host = re.split(":|@",arguments["<args>"])
            RepoMySQL().init_db(host = db_host, root_password = db_password)

    if arguments["site"]:
        if command == "add":
            Injector(db_user = db_user, db_password = db_password,database = db).add_site(arguments["<args>"])
        if command == "list":
            for i in Injector(db_user = db_user, db_password = db_password,database = db).get_sites(): logging.info(i)
                
    if arguments["group"]:
        if command == "import":
            site = injector.get_obj(Site,arguments["<args>"])
            data = Crawler.create_client(site).get_groups()
            injector.insert_data(Parser.parse_groups(data,site.server_type))
            logging.info("total imported groups {}".format(len(data)))

if __name__ == '__main__':
    main()