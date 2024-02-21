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
		student_id AS rowid,
		Students.*,
		Students.last_name || ' ' || Students.first_name AS student_name,
		Parents.last_name || ' ' || Parents.first_name AS parent_name,
		phone,
		email,
		GroupsView.name AS group_name,
		GroupsView.level AS group_level
	FROM Students
		LEFT JOIN parents ON Students.parent_id = Parents.parent_id
		LEFT JOIN GroupsView ON Students.group_id = GroupsView.group_id;

CREATE TABLE Teachers (
	teacher_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name  TEXT
);

CREATE VIEW TeachersView AS
	SELECT
		Teachers.teacher_id AS rowid,
		Teachers.*,
		GROUP_CONCAT(Groups.group_id, ',') AS groups
	FROM teachers
		LEFT JOIN GroupTeachers ON Teachers.teacher_id = Groupteachers.teacher_id
		LEFT JOIN Groups ON GroupTeachers.group_id = Groups.group_id
	GROUP BY Teachers.rowid;

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
		Groups.group_id as rowid,
		Groups.*,
		GroupLevels.name AS level,
		COUNT() AS members 
	FROM Groups
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

CREATE VIEW PaymentsView AS
	SELECT payment_id AS rowid, *
	FROM Payments
	LEFT JOIN Students ON Payments.student_id = Students.student_id;

CREATE VIEW ReportView AS
	SELECT
		Students.parent_id, names, IFNULL(paid, 0) AS paid, due
	FROM (
		SELECT
			parent_id,
			GROUP_CONCAT(student_name, ', ') AS names,
			COUNT() * 3 * 950 - IIF(COUNT() > 1, 150 * COUNT(), 0) AS due
		FROM StudentsView GROUP BY StudentsView.parent_id
	) AS Students
	LEFT JOIN (
		SELECT
		parent_id, SUM(sum / 100) AS paid
		FROM Payments
		LEFT JOIN Students ON Payments.student_id = Students.student_id
		WHERE parent_id IS NOT NULL
		GROUP BY parent_id
	) AS Payments ON Students.parent_id = Payments.parent_id
	GROUP BY Students.parent_id;
