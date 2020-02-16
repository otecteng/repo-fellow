"""repo crawler via command-line.

Usage:
    repo-fellow db <command> [<args>]
    repo-fellow site <command> [<args>]
    repo-fellow project <command> [--site=<id>] [--since=<id>] [--private] [<args>]
    repo-fellow user <command> [--site=<id>] [<args>]
    repo-fellow group <command> [--site=<id>] [<args>]       
    repo-fellow commit <command> [--site=<id>] [<args>]
    repo-fellow event <command> [--site=<id>] [<args>]
    repo-fellow pr <command> [--site=<id>] [<args>]
    repo-fellow tag <command> [--site=<id>] [--since=<id>] [--project=<id>]
    repo-fellow release <command> [--site=<id>] [<args>]

Options: 
    -h,--help 
    --site=<id>   repo site id
    --since=<id>  since object iid
    --project=<id>  project iid
    --private     processing private projects

Example:
    repo-fellow db init root:xxx@localhost
    repo-fellow site add https://user:password@site?name&type
    repo-fellow projects remote owner
    repo-fellow projects list
    repo-fellow projects import site_id
    repo-fellow commit update *
    repo-fellow commit update project
    repo-fellow user import
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
from repofellow.injector import Injector,Commit,Site,Project
from repofellow.parser import Parser
from repofellow.repo_mysql import RepoMySQL

def get_arg(key,default_value = None, args = None):
    if key in os.environ:
        return os.environ[key]
    if args and key in args:
        return args[key]
    return default_value

def parse_projects_args(arguments,injector):
    if arguments["--project"]:
        projects = [injector.get_obj(Project,arguments["--project"])]
    if arguments["--since"]:
        projects = injector.get_projects( site = arguments["--site"],since = arguments["--since"])
    return projects

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
            return
        site = injector.get_obj(Site,arguments["--site"])
        if command == "remote":
            commits = Crawler.create_client(site).getAllProjectCommitsCount("china")
            for i in commits:
                if i["ref"]:
                    logging.info("{}:{}".format(i["name"],i["ref"]["target"]["history"]["totalCount"]))
                else:
                    logging.error("{} has none history record".format(i["name"]))
            return
        injector = Injector(db_user = db_user, db_password = db_password,database = db)                    
        if command == "import":    
            data = Crawler(site,injector).import_projects(arguments["--private"])
            logging.info("total imported projects {}".format(len(data)))
        if command == "update":
            data = Crawler(site,injector).update_projects(arguments["--since"])
        if command == "stat":
            data = Crawler(site,injector).statistic_projects(arguments["--since"])


    if arguments["user"]:
        site = injector.get_obj(Site,arguments["--site"])
        if command == "import":
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
            site = injector.get_obj(Site,arguments["--site"])
            logging.info("importing tags of {}".format(site.name))
            projects = parse_projects_args(arguments,injector)
            Crawler(site,injector).import_commits(projects)
        return
                
    if arguments["tag"]:
        if command == "import":
            site = injector.get_obj(Site,arguments["--site"])
            logging.info("importing tags of {}".format(site.name))
            projects = parse_projects_args(arguments,injector)
            Crawler(site,injector).get_tags(projects)
        return

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