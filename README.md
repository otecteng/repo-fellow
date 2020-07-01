# Usage  

1.How to use the package  
1.1 Init database  
```
repofellow db init --conn=user:password@host
```

1.2 Set db access in env  
```
export FELLOW_USER=xxx
export FELLOW_DB=xxx
export FELLOW_PASSWORD=xxx
```

1.3 Create site  
```
repofellow site add "https://user:token@site?name&type"
repofellow site list
```
token: repo private access token  
site: url, host only  
name:  
type: github or gitlab  

1.4 get site developers and groups
```
repofellow user import --site=site_iid
repofellow group import --site=site_iid
```

1.5 get site projects  
```
nohup repofellow project import --site=site_iid &
repofellow project import --site=site_iid --private
```

1.6 get project size and statistic  
```
repofellow project update --site=site_iid --since=iid
repofellow project contributor --site=site_iid --since=iid
repofellow project stat --site=site_iid --since=iid
repofellow project commits --site=site_iid --since=iid

```
update: get size,pushed date  
stat: get weekly commit count of previos year  
commits: get total commits pages of project  

1.7 get project commits  
```
repofellow commit import --site=site_iid [--since=iid] [--project=project_iid] [--limit=200]
repofellow tag import --site=site_iid [--since=iid]
repofellow release import --site=site_iid [--since=iid]
repofellow branch import --site=site_iid [--since=iid]
repofellow commit style --site=site_iid --since=iid --style="(.*)#(.*)\s+(.*):\s+(.*?)"
```

# Develop  
## Version Requirement  
Python 3.7  
MySQL 5.7

## Install depemdency
```
pip3 install -r requirements.txt
```

## Run from source code
```
python3 -m repofellow 
```

