use rss_feeds;

drop table embeddings;
drop table metadata;
drop table summary;

CREATE TABLE summary (
    id int NOT NULL AUTO_INCREMENT,
    summary TEXT (65535) NOT NULL,
    PRIMARY KEY (id)
); 
CREATE TABLE metadata (
    category VARCHAR(255) NOT NULL,
    sub_category VARCHAR(255) NOT NULL,
    url VARCHAR (255) NOT NULL,
    title VARCHAR (255) NOT NULL,
    summary_id int NOT NULL AUTO_INCREMENT,
    date_published date,
    FOREIGN KEY (summary_id) REFERENCES  summary(id)
); 

CREATE TABLE embeddings (
    summary_id int NOT NULL AUTO_INCREMENT ,
    vector BLOB (65535) NOT NULL,
    FOREIGN KEY (summary_id) REFERENCES  summary(id)
); 