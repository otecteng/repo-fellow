# -*- coding: UTF-8 -*-
import re
import json
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Float, DateTime,Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
import logging
from repofellow.safe_parser import Convertor

Base = declarative_base()
class Project(Base):
    __tablename__ = 'project'
    iid = Column(Integer, primary_key=True)    
    oid = Column(Integer)
    site = Column(Integer)
    path = Column(String(64))
    private = Column(Boolean)
    description = Column(String(512))
    owner = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pushed_at = Column(DateTime)
    language = Column(String(64))
    size = Column(Integer)
    participation = Column(Integer)
    commits = Column(Integer)
    
    def __init__(self,data = None):
        if data:
            self.oid = data["id"]
            self.path = data["path_with_namespace"]
            self.created_at = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
            self.updated_at = datetime.datetime.strptime(data["last_activity_at"][:19], "%Y-%m-%dT%H:%M:%S")
            self.owner = data["owner"]["username"]

    def __str__(self):
        return "{}\t{}\t{}".format(self.path,self.created_at,self.updated_at)

    @staticmethod
    def from_github(data,ret = None):
        if ret is None:
            ret = Project()
        if len(data) == 0:
            logging.warning("empty data, project {}".format(ret.iid))
            return ret
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"full_name","path")
        Convertor.json2db(data,ret,"updated_at")
        Convertor.json2db(data,ret,"created_at")
        Convertor.json2db(data,ret,"description")
        Convertor.json2db(data,ret,"pushed_at")
        Convertor.json2db(data,ret,"language")
        Convertor.json2db(data,ret,"size")
        Convertor.json2db(data,ret,"private")
        if "owner" in data and data["owner"]:
            ret.owner = data["owner"]["login"]
        return ret

    @staticmethod
    def statistic_github(data,ret):
        if "all" in data and data["all"]:
            ret.participation = sum(data["all"])
        return ret

    @staticmethod
    def from_gitee(data,ret = None):
        if ret is None:
            ret = Project()
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"full_name","path")
        Convertor.json2db(data,ret,"updated_at")
        Convertor.json2db(data,ret,"created_at")
        Convertor.json2db(data,ret,"description")
        Convertor.json2db(data,ret,"pushed_at")
        Convertor.json2db(data,ret,"language")
        Convertor.json2db(data,ret,"size")
        Convertor.json2db(data,ret,"private")
        if "owner" in data and data["owner"]:
            ret.owner = data["owner"]["login"]
        return ret

    @staticmethod
    def from_gitlab(data,ret = None):
        if not "owner" in data:
            print("[INFO]:empty owner {}".format(data["path_with_namespace"]))
            data["owner"] = {"username":""}
        return Project(data)

class Site(Base):
    __tablename__ = 'site'
    iid = Column(Integer, primary_key=True)    
    name = Column(String(64))
    server_type = Column(String(64))
    url = Column(String(64))
    token = Column(String(64))
    created_at = Column(DateTime)
    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}".format(self.iid,self.name,self.server_type,self.url,self.created_at)

class Group(Base):
    __tablename__ = 'developer_group'
    iid = Column(Integer, primary_key=True)    
    name = Column(String(64))
    oid = Column(Integer)
    site = Column(Integer)
    location = Column(String(64))
    repo_count = Column(Integer)
    created_at = Column(DateTime)
    def __str__(self):
        return "{}\t{}\t{}\t{}".format(self.iid,self.name,self.repo_count,self.location)

    @staticmethod
    def from_github(data):
        ret = Group()
        ret.name = data["name"]
        ret.location = data["location"]
        ret.description = data["description"]
        if data["repositories"]:
            ret.repo_count = data["repositories"]["totalCount"]
        return ret

class CommitFile(Base):
    __tablename__ = 'commit_file'
    iid = Column(Integer, primary_key=True)
    commit_iid = Column(Integer)
    commit_id = Column(String(64))
    id = Column(String(64))
    filename = Column(String(128))
    status = Column(String(64))
    additions = Column(Integer)
    deletions = Column(Integer)
    changes = Column(Integer)
    def __init__(self,data):
        self.path = data["path_with_namespace"]
        self.created_at = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.updated_at = datetime.datetime.strptime(data["last_activity_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.owner = data["owner"]["username"]

class Commit(Base):
    __tablename__ = 'commit'
    iid = Column(Integer, primary_key=True)
    id = Column(String(64))
    project = Column(String(128))
    author_name = Column(String(64))
    author_email = Column(String(64))
    message = Column(String(1024))
    created_at = Column(DateTime)
    additions = Column(Integer)
    deletions = Column(Integer)
    total = Column(Integer)
    issue = Column(String(64))
    style_checked = Column(Boolean)
    site = Column(Integer)
    project_oid = Column(Integer)
    oid = Column(Integer)
    
    def __init__(self,data):
        self.id = data["id"]
        self.message = data["message"].rstrip()[:1000]
        self.author_name = data["author_name"]
        self.author_email = data["author_email"][:64]
        self.created_at = data["authored_date"]
    
    @staticmethod
    def find_issue(message):
        if message is None:
            return None
        issue = None
        start = message.find('#')
        if  start  < 1 :
            return None
        issue = message[start + 1:]
        pos = issue.find(' ')
        if pos > 1 :
            issue = issue[0:pos]
        pos = issue.find(':')
        if pos > 1 :
            issue = issue[0:pos]
        pos = issue.find('：')
        if pos > 1 :
            issue = issue[0:pos]
        return issue[:64]

    def __str__(self):
        return "{}[{}]:{}".format(self.created_at,self.author_email,self.message)

    @staticmethod
    def from_gitee(data):
        # sample: date: 2019-11-24T23:22:06.000+08:00
        data["commit"]["author"]["date"] = datetime.datetime.strptime(data["commit"]["author"]["date"][:19], "%Y-%m-%dT%H:%M:%S")
        author = data["commit"]["author"]
        content = {"author_name":author["name"],"author_email":author["email"],"authored_date":author["date"],"message":data["commit"]["message"]}
        return Commit(content)

    @staticmethod
    def from_gitlab(data,project = project):
        # sample: authored_date: 2019-11-24T23:22:06.000+08:00
        data["authored_date"] = datetime.datetime.strptime(data["authored_date"][:19], "%Y-%m-%dT%H:%M:%S")
        ret = Commit(data)
        ret.project = project
        return ret

    @staticmethod
    def from_github(data,project = project):
        data["commit"]["committer"]["date"] = datetime.datetime.strptime(data["commit"]["committer"]["date"][:19], "%Y-%m-%dT%H:%M:%S")
        author = data["commit"]["committer"]
        content = {"id":data["sha"],
            "author_name":author["name"],"author_email":author["email"],"authored_date":author["date"],
            "message":data["commit"]["message"][:1000]
        }
        ret = Commit(content)
        # ret.issue = Commit.find_issue(content["message"])
        ret.project = project
        return ret

    def load_github_stat(self,data):
        self.total = data["stats"]["total"]
        self.additions = data["stats"]["additions"]
        self.deletions = data["stats"]["deletions"]
        return self

    @staticmethod
    def append_count_github(commit,data):
        commit.additions = data["stats"]["additions"]
        commit.deletions = data["stats"]["deletions"]
        commit.total = data["stats"]["total"]
        return commit

    def style_check(self,style = None):
        if style is None:
            style = r'(.*)#(.*)\s+(.*):\s+(.*?)'
        self.style_checked = (re.match(style, self.message, flags=0) is not None)
        return self

class Event(Base):
    __tablename__ = 'project_event'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    project = Column(String(128))
    project_oid = Column(Integer)
    site = Column(Integer)
    author = Column(String(64))
    event_type = Column(String(64))
    description = Column(String(1024))
    created_at = Column(DateTime)

    def __init__(self,project = None):
        self.created_at = datetime.datetime.now()
        if project is not None:
            self.project = project.path
            self.project_oid = project.oid
            self.site = project.site

    def __str__(self):
        return "{}[{}]:{}({})".format(self.created_at,self.author,self.project,self.event_type)

    @staticmethod
    def from_github(data, project = None, ret = None):
        if ret is None:
            ret = Event(project)
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"type","event_type")
        Convertor.json2db(data,ret,"created_at")
        if "actor" in data and data["actor"]:
            ret.author = data["actor"]["login"]
        data["author"]={"username":data["actor"]["login"]}
        if "payload" in data and data["payload"]:
            if "commits" in data["payload"] and data["payload"]["commits"]:
                ret.description = "commits_size={};author_email={};author_name={}".format(
                    data["payload"]["size"],data["payload"]["commits"][0]["author"]["email"],data["payload"]["commits"][0]["author"]["name"])
        return ret

    @staticmethod
    def from_gitlab(data):
        data["created_at"] = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        return Event(data)

def safe_value(data,json_path,db_field):
    if json_path in data and data[json_path]:
        return data[json_path][:60]
    return None

class Developer(Base):
    __tablename__ = 'developer'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    site = Column(Integer)
    username = Column(String(64))
    name = Column(String(64))
    email = Column(String(64))
    repo_count = Column(Integer)
    created_at = Column(DateTime)

    @staticmethod
    def from_github(data, obj = None):
        ret = Developer()
        if obj:
            ret = obj
        if "repositories" in data:
            ret.username = data["login"]
            ret.name = data["name"]
            ret.location = data["location"]
            if data["repositories"]:
                ret.repo_count = data["repositories"]["totalCount"]
        else:
            Convertor.json2db(data,ret,"id","oid")
            Convertor.json2db(data,ret,"username","login")
            Convertor.json2db(data,ret,"name")
            Convertor.json2db(data,ret,"email")
            Convertor.json2db(data,ret,"created_at")
        return ret

    @staticmethod
    def from_gitlab(data):
        ret = Developer()
        ret.oid,ret.username,ret.name = data["id"],data["username"],data["name"]
        return ret
        
class Pull(Base):
    __tablename__ = 'pull'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    project = Column(String(64))
    state = Column(String(64))
    title = Column(String(512))
    user = Column(String(64))
    head = Column(String(512))
    base = Column(String(512))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    site = Column(Integer)
    
    def from_github(data,ret = None):
        if ret is None:
            ret = Pull()
        Convertor.json2db(data,ret,"state")
        Convertor.json2db(data,ret,"title")
        Convertor.json2db(data,ret,"created_at")
        Convertor.json2db(data,ret,"updated_at")
        if "user" in data and data["user"]:
            ret.user = data["user"]["login"]
        if "head" in data and data["head"]:
            ret.head = data["head"]["sha"]
        if "base" in data and data["base"]:
            ret.base = data["base"]["sha"]
        return ret

    def from_gitlab(data,ret = None):
        if ret is None:
            ret = Pull()
        Convertor.json2db(data,ret,"state")
        Convertor.json2db(data,ret,"title")
        Convertor.json2db(data,ret,"created_at")
        Convertor.json2db(data,ret,"updated_at")
        if "author" in data and data["author"]:
            ret.user = data["author"]["username"]
        return ret

class Branch(Base):
    __tablename__ = 'project_branch'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    site = Column(Integer)
    project_oid = Column(Integer)
    project = Column(String(64))
    created_at = Column(DateTime)
    name = Column(String(64))
    protected = Column(Boolean)

    def from_github(data,ret = None):
        if ret is None:
            ret = Branch()
        Convertor.json2db(data,ret,"name")
        Convertor.json2db(data,ret,"protected")
        return ret

class Tag(Base):
    __tablename__ = 'tag'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    site = Column(Integer)
    project_oid = Column(Integer)
    project = Column(String(64))
    created_at = Column(DateTime)
    name = Column(String(64))
    commit = Column(String(64))

    def from_github(data,ret = None):
        if ret is None:
            ret = Tag()
        Convertor.json2db(data,ret,"name")
        if "commit" in data and data["commit"]:
            ret.commit = data["commit"]["sha"]
        return ret

class Release(Base):
    __tablename__ = 'project_release'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    project = Column(String(64))
    project_oid = Column(Integer)
    created_at = Column(DateTime)
    name = Column(String(64))
    tag = Column(String(64))

    def from_github(data,ret = None):
        if ret is None:
            ret = Release()
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"name")
        Convertor.json2db(data,ret,"tag_name","tag")
        Convertor.json2db(data,ret,"created_at")
        if "author" in data and data["author"]:
            ret.author = data["author"]["login"]
        else:
            logging.info("missing author")
        return ret

class Contributor(Base):
    __tablename__ = 'contributor'
    iid = Column(Integer, primary_key=True)    
    project = Column(String(64))
    project_oid = Column(Integer)
    developer = Column(String(64))
    developer_oid = Column(Integer)
    site = Column(Integer)
    contribution = Column(Integer)
    created_at = Column(DateTime)

    @staticmethod
    def from_github(data,project):
        ret = []
        for i in data:
            c = Contributor(i,project)
            c.contribution = i["contributions"]
            c.developer = i["login"]
            c.developer_oid = i["id"]
            ret.append(c)
        return ret

    @staticmethod
    def from_gitee(data,project):
        ret = []
        for i in data:
            c = Contributor(i,project)
            c.contribution = i["contributions"]
            c.developer = i["name"]
            ret.append(c)
        return ret

    def __init__(self,json_data,project):
        self.project = project.path
        self.project_oid = project.oid
        self.site = project.site

    def __str__(self):
        return "{}<={}[{}]".format(self.project,self.developer,self.contribution)

class Injector:
    def __init__(self,db_user = "repo", db_password = "", host = "localhost", database = "repo_fellow"):
        self.engine = create_engine("mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8mb4".format(db_user,db_password,host,database))
        DBSession = sessionmaker(bind = self.engine)
        self.db_session = DBSession()
        Convertor.load_schema(Project())
        Convertor.load_schema(Tag())
        Convertor.load_schema(Release())
        Convertor.load_schema(Developer())
    
    def insert_data(self,data):
        for i in data:
            self.db_session.add(i)
        self.db_session.commit()
    
    def get_projects(self,since = None, site = None, ids = None):
        if ids:
            return list(map(lambda x:self.db_session.query(Project).get(x),ids))
        if since and site:
            return self.db_session.query(Project).filter(Project.site == site).filter(Project.iid > since)
        if site:
            return self.db_session.query(Project).filter(Project.site == site)
        return self.db_session.query(Project)

    def get_users(self,since = None, until = None, site = None):
        ret = self.db_session.query(Developer)
        if since:
            ret = ret.filter(Developer.iid >= int(since))
        if until:
            ret = ret.filter(Developer.iid < int(until))
        if site:
            ret = ret.filter(Developer.site == site)
        return ret.all()

    def get_contributors(self,site,filter = None):
        if filter:
            print(filter)
            return self.db_session.query(Contributor).filter(Contributor.site == site.iid).filter(Contributor.project.like("%{}%".format(filter))).all()    
        return self.db_session.query(Contributor).filter(Contributor.site == site.iid).all()

    def get_project(self,path):
        return self.db_session.query(Project).filter(Project.path == path).first()

    def get_obj(self,type,iid):
        return self.db_session.query(type).get(iid)

    def list_obj(self,type,filter = None):
        if filter:
            return self.db_session.query(type).filter(filter).all()
        return self.db_session.query(type).all()

    def get_commits(self,project = None):
        if project:
            return self.db_session.query(Commit).filter(Commit.project == project.path)
        else:
            return self.db_session.query(Commit)

    def get_project_last_commit(self,path):
        return self.db_session.query(Commit).filter(Commit.project == path).order_by(Commit.created_at.desc()).first()

    def db_commit(self):
        self.db_session.commit()

    def add_site(self,site_url):
        # http://user:password@url?name&type
        args = re.split(":|#|@|\?|&",site_url)
        site = Site()
        site.name,site.user,site.token,site.url,site.server_type = args[4],args[1][2:-1],args[2],"{}://{}".format(args[0],args[3]),args[5]
        self.db_session.add(site)
        self.db_session.commit()
        logging.info("server added, iid = {}".format(self.db_session.query(Site).filter(Site.name == site.name).first().iid))

    def get_sites(self):
        return self.db_session.query(Site)