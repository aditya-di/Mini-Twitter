BEGIN TRANSACTION;
DROP TABLE IF EXISTS  activeUsers;
DROP TABLE IF EXISTS followers;
DROP TABLE IF EXISTS userTimeline;
CREATE TABLE activeUsers(
  userID INTEGER primary key,
  userName TEXT NOT NULL UNIQUE,
  emailID TEXT,
  password TEXT);

CREATE TABLE IF NOT EXISTS followers(
  followerUser TEXT,
  followedUser TEXT,
  FOREIGN KEY (followerUser)REFERENCES activeUsers(userName));

CREATE TABLE userTimeline (
    userName TEXT,
    postText Text,
    postedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userName)REFERENCES activeUsers(userName));

COMMIT;
