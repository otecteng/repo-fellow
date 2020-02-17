import logging
from repofellow.injector import Project,Commit,CommitFile,Event,Developer,Group

class Parser:
    @staticmethod
    def json_to_db(data,db_class, format="github", site = None, project = None):
        func = getattr(db_class, "from_{}".format(format))
        if func is None:
            logging.error("can not find function {} in {}".format("from_{}".format(format),db_class))
            return []
        ret = [func(i) for i in data]
        if site is not None:
            [setattr(i,"site",site.iid) for i in ret]
        if project is not None:
            [setattr(i,"project",project.path) for i in ret]
        return ret

    @staticmethod
    def parse_events(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Event.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Event.from_gitlab(x),data))
        else:
            return list(map(lambda x:Event.from_github(x),data))

    @staticmethod
    def parse_projects(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Project.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Project.from_gitlab(x),data))
        else:
            return list(map(lambda x:Project.from_github(x),data))

    @staticmethod
    def parse_users(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Developer.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Developer.from_gitlab(x),data))
        else:
            return list(map(lambda x:Developer.from_github(x),data))

    @staticmethod
    def parse_groups(data,format="github"):
        if format == "gitee":
            return list(map(Group.from_gitee,data))
        elif format == "gitlab":
            return list(map(Group.from_gitlab,data))
        else:
            return list(map(Group.from_github,data))
