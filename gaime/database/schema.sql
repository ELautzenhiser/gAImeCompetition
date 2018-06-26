DROP DATABASE IF EXISTS gaime;

CREATE DATABASE gaime;

USE gaime;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(30) NOT NULL,
    password VARCHAR(30) NOT NULL,
    privileges TINYINT NOT NULL DEFAULT 0,
    fname VARCHAR(30),
    lname VARCHAR(30),
    created_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status enum('Active','Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (user_id)
);

CREATE TABLE Languages (
    language_id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(30) NOT NULL,
    PRIMARY KEY (language_id)
);

CREATE TABLE Games (
    game_id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(30) NOT NULL,
    created_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    min_num_players INT NOT NULL,
    max_num_players INT NOT NULL,
    author_id INT NOT NULL,
    doc_file VARCHAR(100) NOT NULL,
    status enum('Published', 'Unpublished', 'Deleted') NOT NULL DEFAULT 'Unpublished',
    FOREIGN KEY (author_id) REFERENCES Users (user_id),
    PRIMARY KEY (game_id)
);

CREATE TABLE Uploads (
    upload_id INT AUTO_INCREMENT NOT NULL,
    filename VARCHAR(100),
    language_id INT NOT NULL,
    game_id INT NOT NULL,
    author_id INT NOT NULL,
    created_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status enum('Published','Unpublished', 'Deleted') NOT NULL DEFAULT 'Unpublished',
    type enum('Player', 'Ref') NOT NULL DEFAULT 'Player',
    PRIMARY KEY (upload_id),
    FOREIGN KEY (language_id) REFERENCES Languages (language_id),
    FOREIGN KEY (game_id) REFERENCES Games (game_id),
    FOREIGN KEY (author_id) REFERENCES Users (user_id)
);

CREATE TABLE Matches (
    match_id INT AUTO_INCREMENT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    game_id INT NOT NULL,
    referee_id INT NOT NULL,
    PRIMARY KEY (match_id),
    FOREIGN KEY (game_id) REFERENCES Games (game_id),
    FOREIGN KEY (referee_id) REFERENCES Uploads (upload_id)
);

CREATE TABLE Match_Players (
	match_id INT NOT NULL,
    player_id INT NOT NULL,
    place INT,
    points INT,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES Matches (match_id),
    FOREIGN KEY (player_id) REFERENCES Uploads (upload_id)
);

CREATE TABLE Moves (
	move_id INT AUTO_INCREMENT NOT NULL,
	match_id INT NOT NULL,
	turn_number INT NOT NULL,
	player_id INT NOT NULL,
	move VARCHAR(255),
	PRIMARY KEY (move_id),
	FOREIGN KEY (match_id) REFERENCES Matches (match_id),
	FOREIGN KEY (player_id) REFERENCES Uploads (upload_id)
);

CREATE TABLE Friendships (
    requester_id INT NOT NULL,
    responder_id INT NOT NULL,
    status ENUM('Sent','Rescinded','Declined','Accepted','Unfriended') NOT NULL,
    request_time DATETIME NOT NULL,
    response_time DATETIME,
    PRIMARY KEY (requester_id, responder_id),
    FOREIGN KEY (requester_id) REFERENCES Users (user_id),
    FOREIGN KEY (responder_id) REFERENCES Users (user_id)
);

INSERT INTO Languages (name) VALUES ('Python 3');

INSERT INTO Users (username, email, password, privileges,
                   fname, created_dt, status)
    VALUES ('gaime_admin', 'admin@gaime.com', 'admin', -1,
            'Admin', '2018-06-15 23:59:59', 'Active');

INSERT INTO Games (name, min_num_players, max_num_players, author_id, doc_file, status)
    VALUES ('Rock Paper Scissors', 2, 2, 1, 'rock_paper_scissors.txt', 'Published');

INSERT INTO Uploads (filename, language_id, game_id, author_id,
                     created_dt, status, type)
    VALUES ('20180618235959_rock_paper_scissors.py', 1, 1, 1,
            '2018-06-18 23:59:59', 'Deleted', 'Player'),
           ('20180619120000_rock_paper_scissors.py', 1, 1, 1,
            '2018-06-19 12:00:00', 'Published', 'Player');
            
