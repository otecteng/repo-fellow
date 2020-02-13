Usage  

1.Setting env  
```  
export GIT_SITE = "https://xxx"  
export GIT_TOKEN = "xxx"  
export GIT_SERVER = "github"  
```

2.Execute crawl projects  
```
repofellow project remote owner
```

Development  
```
python3 -m repofellow project remote owner
```

Build  
```
python3 setup.py sdist bdist_wheel
```

for ubuntu 16  
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