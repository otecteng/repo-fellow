CREATE DATABASE IF NOT EXISTS repo_fellow;
USE repo_fellow;
CREATE USER IF NOT EXISTS 'repo'@'%' IDENTIFIED BY 'fellow';
GRANT ALL PRIVILEGES ON repo_fellow.* TO 'repo'@'%';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS `project`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,    
  oid     BIGINT,
  path      VARCHAR(64),
  owner     VARCHAR(512),
  site      Integer,
  created_at     DATETIME,
  updated_at     DATETIME
);

CREATE TABLE IF NOT EXISTS `commit`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,    
  id      VARCHAR(64),
  project  VARCHAR(128),
  message  VARCHAR(1024),
  created_at    DATETIME,
  author_name   VARCHAR(64),
  author_email  VARCHAR(64),
  additions Integer,
  deletions Integer,
  total Integer,
  issue  VARCHAR(64)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `commit_file`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  id      VARCHAR(64),
  commit_iid Integer,
  commit_id  VARCHAR(64),
  filename  VARCHAR(256),
  status  VARCHAR(1024),
  additions    Integer,
  deletions   Integer,
  changes  Integer
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `pull`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  oid     BIGINT,
  project      VARCHAR(64),
  created_at    DATETIME,
  updated_at    DATETIME,
  state  VARCHAR(64),
  title  VARCHAR(512),
  user  VARCHAR(64),
  head  VARCHAR(64),
  base  VARCHAR(64)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `tag`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  oid     BIGINT,
  project      VARCHAR(64),
  created_at    DATETIME,
  updated_at    DATETIME,
  name  VARCHAR(64),
  commit  VARCHAR(64)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `release`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  oid     BIGINT,
  project      VARCHAR(64),
  created_at    DATETIME,
  updated_at    DATETIME,
  name  VARCHAR(64),
  tag  VARCHAR(64),
  author  VARCHAR(64)
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `developer`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  oid     BIGINT,
  username      VARCHAR(64),
  name  VARCHAR(64),
  email  VARCHAR(64),
  site      Integer,  
  created_at    DATETIME
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `site`
(
  iid     BIGINT PRIMARY KEY AUTO_INCREMENT,
  name  VARCHAR(64),
  server_type  VARCHAR(64),  
  url      VARCHAR(64),  
  token  VARCHAR(64),
  created_at    DATETIME
)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

