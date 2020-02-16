#Usage  

1.How to use the package
1.1 Init database  
```
repofellow db init user:password@host
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
token: repo private access tokem  
site: url, host only  
name:  
type: github or gitlab  

1.4 get site developers
```
repofellow user import --site=site_iid
```

1.5 get site projects  
```
repofellow project import --site=site_iid
repofellow project import --site=site_iid --private
```

1.6 get project size and statistic  
```
repofellow project update --site=site_iid 
repofellow project stat --site=site_iid [--since=iid]
repofellow project commits --site=site_iid [--since=iid]
```

1.7 get project commits  
```
repofellow commit import --site=site_iid [--since=iid]
repofellow commit import --site=site_iid --project=project_iid
repofellow tag import --site=site_iid [--since=iid]
```


#Build  
```
python3 setup.py sdist bdist_wheel
```

##For ubuntu 16  
```
export LC_ALL=C
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.7
sudo ln -s /usr/local/bin/python3.7 /usr/bin/python3
pip3 install wheel
sudo apt-get install python3.7-gdbm
```