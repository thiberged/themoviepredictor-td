CREATE TABLE `movies` (
	`id` int NOT NULL AUTO_INCREMENT,
	`title` varchar(255) NOT NULL,
	`original_title` varchar(255) NOT NULL,
	`synopsis` TEXT DEFAULT NULL,
	`duration` int NOT NULL,
	`rating` enum('TP', '-12', '-16', '-18') NOT NULL,
	`production_budget` int DEFAULT NULL,
	`marketing_budget` int DEFAULT NULL,
	`release_date` DATE NOT NULL,
	`3d` bool NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`)
);

CREATE TABLE `people` (
	`id` int NOT NULL AUTO_INCREMENT,
	`firstname` varchar(255) NOT NULL,
	`lastname` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

INSERT INTO `movies` 
    (`title`, `original_title`, `duration`, `rating`, `release_date`)
VALUES
    ('Joker', 'Joker', 122, '-12', '2019-10-09')
;

INSERT INTO `people`
    (`firstname`, `lastname`)
VALUES
    ('Joaquin', 'Phoenix'),
    ('Todd', 'Phillips'),
    ('Scott', 'Silver')
;