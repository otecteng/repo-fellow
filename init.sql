CREATE DATABASE IF NOT EXISTS repo_fellow;
USE repo_fellow;
CREATE USER IF NOT EXISTS 'repo'@'%' IDENTIFIED BY 'fellow';
GRANT ALL PRIVILEGES ON repo_fellow.* TO 'repo'@'%';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS `project`
(
  path  VARCHAR(64) PRIMARY KEY,
  owner  VARCHAR(512),
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

CREATE TABLE IF NOT EXISTS `commit_files`
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

