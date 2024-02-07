CREATE TABLE Users (
	user_id  INTEGER PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL
);

CREATE TABLE Parents (
	parent_id  INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name  TEXT NOT NULL,
	phone      TEXT NOT NULL,
	email      TEXT NOT NULL
);

CREATE TABLE Students (
	student_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name  TEXT NOT NULL,
	group_id   INTEGER,
	parent_id  INTEGER,
	FOREIGN KEY (group_id) REFERENCES Groups (group_id),
	FOREIGN KEY (parent_id) REFERENCES Parents (parent_id)
);

CREATE VIEW StudentsView AS
	SELECT 
		student_id,
		Students.last_name || ' ' || Students.first_name AS student_name,
		Parents.parent_id,
		Parents.last_name || ' ' || Parents.first_name AS parent_name,
		phone,
		email,
		GroupsView.group_id,
		GroupsView.name AS group_name,
		GroupsView.level AS group_level
	FROM students
		LEFT JOIN parents ON Students.parent_id = Parents.parent_id
		LEFT JOIN GroupsView ON Students.group_id = GroupsView.group_id;

CREATE TABLE Teachers (
	teacher_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name  TEXT
);

CREATE TABLE Groups (
	group_id INTEGER PRIMARY KEY,
	name     TEXT NOT NULL,
	level_id INTEGER,
	FOREIGN KEY (level_id) REFERENCES GroupLevels (level_id)
);

CREATE TABLE GroupLevels (
	level_id INTEGER PRIMARY KEY,
	name     TEXT NOT NULL
);

CREATE TABLE GroupTeachers (
	teacher_id INTEGER,
	group_id   INTEGER,
	FOREIGN KEY (teacher_id) REFERENCES Teachers (teacher_id),
	FOREIGN KEY (group_id) REFERENCES Groups (group_id)
);

CREATE VIEW GroupsView AS
	SELECT
		Groups.*,
		GroupLevels.name AS level,
		COUNT() AS members 
	FROM groups
		LEFT JOIN GroupLevels ON Groups.level_id = GroupLevels.level_id
		LEFT JOIN students ON Groups.group_id = Students.group_id
			GROUP BY Groups.rowid;

CREATE TABLE Payments (
	payment_id INTEGER PRIMARY KEY,
	payer      TEXT NOT NULL,
	title      TEXT NOT NULL,
	sum        INTEGER NOT NULL,
	date       TEXT,
	student_id INTEGER,
	FOREIGN KEY (student_id) REFERENCES Students (student_id)
);
