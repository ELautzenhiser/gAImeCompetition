SET foreign_key_checks=0;
DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
	user_id INT AUTO_INCREMENT NOT NULL,
        username TEXT UNIQUE NOT NULL,
	email VARCHAR(30) NOT NULL,
	password VARCHAR(30) NOT NULL,
	privileges TINYINT NOT NULL DEFAULT 0,
	fname VARCHAR(30),
	lname VARCHAR(30),
	created_dt DATETIME NOT NULL,
	active enum('A','I') NOT NULL DEFAULT 'A',
	PRIMARY KEY (user_id)
	);

DROP TABLE IF EXISTS Languages;	
CREATE TABLE Languages (
	language_id INT AUTO_INCREMENT NOT NULL,
	name VARCHAR(30) NOT NULL,
	PRIMARY KEY (language_id)
	);
	
DROP TABLE IF EXISTS Games;
CREATE TABLE Games (
	game_id INT AUTO_INCREMENT NOT NULL,
	name VARCHAR(30) NOT NULL,
        created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	max_num_players INT NOT NULL,
	default_player INT,
        author INT NOT NULL,
        FOREIGN KEY (author_id) REFERENCES Users (user_id),
	PRIMARY KEY (game_id)
	);

DROP TABLE IF EXISTS Players;
CREATE TABLE Players (
	player_id INT AUTO_INCREMENT NOT NULL,
	file_location VARCHAR(30),
	language_id INT NOT NULL,
	game_id INT NOT NULL,
	author_id INT NOT NULL,
	created_dt DATETIME NOT NULL,
	PRIMARY KEY (player_id),
	FOREIGN KEY (language_id) REFERENCES Languages (language_id),
	FOREIGN KEY (game_id) REFERENCES Games (game_id),
	FOREIGN KEY (author_id) REFERENCES Users (user_id)
	);
	
ALTER TABLE Games ADD CONSTRAINT FOREIGN KEY (default_player) REFERENCES Players (player_id);

DROP TABLE IF EXISTS Matches;
CREATE TABLE Matches (
	match_id INT AUTO_INCREMENT NOT NULL,
	start_time DATETIME NOT NULL,
	end_time DATETIME,
	game_id INT NOT NULL,
	PRIMARY KEY (match_id),
	FOREIGN KEY (game_id) REFERENCES Games (game_id)
	);

DROP TABLE IF EXISTS Friendships;
CREATE TABLE Friendships (
	requester_id INT NOT NULL,
	responder_id INT NOT NULL,
	status ENUM('S','R','D','A','U') NOT NULL,
	request_time DATETIME NOT NULL,
	response_time DATETIME,
	PRIMARY KEY (requester_id, responder_id),
	FOREIGN KEY (requester_id) REFERENCES Users (user_id),
	FOREIGN KEY (responder_id) REFERENCES Users (user_id)
	);
	
SET foreign_key_checks=1;
	
INSERT INTO Languages (name) VALUES ('Python 3');

INSERT INTO Games (name, max_num_players) VALUES ('Rock Paper Scissors', 2);
