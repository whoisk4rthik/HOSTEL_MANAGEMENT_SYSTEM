-- ============================================================
-- 🚩 HOSTEL MANAGEMENT SYSTEM - DATABASE SETUP
-- This script creates the database, tables, sample data,
-- and the custom functions, procedures, and triggers.
-- ============================================================

-- 1. DATABASE CREATION
CREATE DATABASE IF NOT EXISTS hostel_db;
USE hostel_db;

-- 2. DDL (TABLE CREATION)

-- WARDEN Table
CREATE TABLE warden (
    Staff_ID INT NOT NULL,
    Name VARCHAR(50) DEFAULT NULL,
    Ph_no VARCHAR(15) DEFAULT NULL,
    PRIMARY KEY (Staff_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MESS Table
CREATE TABLE mess (
    Mess_ID INT NOT NULL,
    Name VARCHAR(50) DEFAULT NULL,
    Type VARCHAR(20) DEFAULT NULL,
    Capacity INT DEFAULT NULL,
    Fees DECIMAL(10,2) DEFAULT NULL,
    Staff_ID INT DEFAULT NULL,
    PRIMARY KEY (Mess_ID),
    KEY Staff_ID (Staff_ID),
    CONSTRAINT mess_ibfk_1 FOREIGN KEY (Staff_ID) 
        REFERENCES warden (Staff_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ROOM Table
CREATE TABLE room (
    Room_ID INT NOT NULL,
    Room_no VARCHAR(10) DEFAULT NULL,
    Capacity INT DEFAULT NULL,
    Status VARCHAR(20) DEFAULT NULL,
    Staff_ID INT DEFAULT NULL,
    PRIMARY KEY (Room_ID),
    KEY Staff_ID (Staff_ID),
    CONSTRAINT room_ibfk_1 FOREIGN KEY (Staff_ID) 
        REFERENCES warden (Staff_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- STUDENT Table
CREATE TABLE student (
    Student_ID INT NOT NULL,
    FirstName VARCHAR(50) DEFAULT NULL,
    LastName VARCHAR(50) DEFAULT NULL,
    Department VARCHAR(50) DEFAULT NULL,
    Sex CHAR(1) DEFAULT NULL,
    Email VARCHAR(100) DEFAULT NULL,
    Room_ID INT DEFAULT NULL,
    Mess_ID INT DEFAULT NULL,
    PRIMARY KEY (Student_ID),
    KEY Room_ID (Room_ID),
    KEY Mess_ID (Mess_ID),
    CONSTRAINT student_ibfk_1 FOREIGN KEY (Room_ID) 
        REFERENCES room (Room_ID),
    CONSTRAINT student_ibfk_2 FOREIGN KEY (Mess_ID) 
        REFERENCES mess (Mess_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- FEES Table (Payment_ID MUST be AUTO_INCREMENT for web payments to work)
CREATE TABLE fees (
    Payment_ID INT NOT NULL AUTO_INCREMENT, -- AUTO_INCREMENT ADDED FOR FIX
    Status VARCHAR(20) DEFAULT NULL,
    FeesAmount DECIMAL(10,2) DEFAULT NULL,
    PaymentDate DATE DEFAULT NULL,
    Type VARCHAR(20) DEFAULT NULL,
    Student_ID INT DEFAULT NULL,
    PRIMARY KEY (Payment_ID),
    KEY Student_ID (Student_ID),
    CONSTRAINT fees_ibfk_1 FOREIGN KEY (Student_ID) 
        REFERENCES student (Student_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- VISITOR Table
CREATE TABLE visitor (
    Visitor_Name VARCHAR(50) NOT NULL,
    Ph_no VARCHAR(15) NOT NULL,
    Relation_to_student VARCHAR(50) DEFAULT NULL,
    VisitDate DATE DEFAULT NULL,
    OutDate DATE DEFAULT NULL,
    PRIMARY KEY (Visitor_Name, Ph_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- VISITEDBY Table
CREATE TABLE visitedby (
    Visitor_Name VARCHAR(50) NOT NULL,
    Student_ID INT NOT NULL,
    PRIMARY KEY (Visitor_Name, Student_ID),
    KEY Student_ID (Student_ID),
    CONSTRAINT visitedby_ibfk_1 FOREIGN KEY (Visitor_Name) 
        REFERENCES visitor (Visitor_Name),
    CONSTRAINT visitedby_ibfk_2 FOREIGN KEY (Student_ID) 
        REFERENCES student (Student_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- STUDENTPHONE Table
CREATE TABLE studentphone (
    Ph_no VARCHAR(15) NOT NULL,
    Student_ID INT NOT NULL,
    PRIMARY KEY (Ph_no, Student_ID),
    KEY Student_ID (Student_ID),
    CONSTRAINT studentphone_ibfk_1 FOREIGN KEY (Student_ID) 
        REFERENCES student (Student_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ROOMALLOCATION Table
CREATE TABLE roomallocation (
    AllocationDate DATE DEFAULT NULL,
    VacateDate DATE DEFAULT NULL,
    Student_ID INT NOT NULL,
    Room_ID INT NOT NULL,
    PRIMARY KEY (Student_ID, Room_ID),
    KEY Room_ID (Room_ID),
    CONSTRAINT roomallocation_ibfk_1 FOREIGN KEY (Student_ID) 
        REFERENCES student (Student_ID),
    CONSTRAINT roomallocation_ibfk_2 FOREIGN KEY (Room_ID) 
        REFERENCES room (Room_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 3. DML (INSERT SAMPLE DATA)

INSERT INTO warden VALUES
(101,'Ravi Kumar','9876543210'), (102,'Anjali Mehta','9823014576'), (103,'Vikram Singh','9867452390'), (104,'Sneha Nair','9812345678'), (105,'Arjun Patel','9890054321'), (106,'Priya Sharma','9834567890'), (107,'Rahul Das','9845098765'), (108,'Neha Reddy','9887766554'), (109,'Karan Verma','9876001234'), (110,'Meera Iyer','9822099999');

INSERT INTO mess VALUES
(1,'Annapurna Mess','Vegetarian',120,2500.00,101), (2,'Gourmet Hub','Non-Vegetarian',100,2800.00,102), (3,'Healthy Bites','Vegetarian',80,2300.00,103), (4,'Spice Delight','Non-Vegetarian',90,2700.00,104), (5,'Green Leaf','Vegetarian',110,2400.00,105), (6,'Royal Feast','Non-Vegetarian',150,3000.00,106), (7,'Campus Tiffins','Vegetarian',75,2200.00,107), (8,'Daily Dine','Mixed',130,2600.00,108), (9,'Savory Spot','Vegetarian',95,2350.00,109), (10,'Flavors Corner','Non-Vegetarian',85,2750.00,110);

INSERT INTO room VALUES
(1,'A101',2,'Occupied',101), (2,'A102',2,'Available',101), (3,'A103',3,'Under Maintenance',102), (4,'B201',2,'Occupied',103), (5,'B202',1,'Available',104), (6,'B203',2,'Occupied',105), (7,'C301',3,'Occupied',106), (8,'C302',2,'Occupied',107), (9,'D401',1,'Under Maintenance',108), (10,'D402',2,'Available',109);

INSERT INTO student VALUES
(201,'Amit','Sharma','CSE','M','amit.sharma@univ.edu',6,1), (202,'Priya','Menon','ECE','F','priya.menon@univ.edu',2,3), (203,'Rohan','Verma','MECH','M','rohan.verma@univ.edu',7,2), (204,'Sneha','Patil','IT','F','sneha.patil@univ.edu',1,4), (205,'Kiran','Reddy','CIVIL','M','kiran.reddy@univ.edu',3,5), (206,'Neha','Gupta','EEE','F','neha.gupta@univ.edu',7,7), (207,'Rahul','Nair','CSE','M','rahul.nair@univ.edu',8,6), (208,'Divya','Iyer','ECE','F','divya.iyer@univ.edu',9,8), (209,'Vivek','Singh','MECH','M','vivek.singh@univ.edu',1,9), (210,'Anjali','Deshmukh','IT','F','anjali.deshmukh@univ.edu',3,10);

INSERT INTO fees VALUES
(301,'Paid',2500.00,'2025-01-15','Mess',201), (302,'Paid',5000.00,'2025-01-16','Hostel',202), (303,'Pending',2300.00,'2025-02-01','Mess',203), (304,'Paid',2700.00,'2025-02-10','Mess',204), (305,'Paid',5200.00,'2025-02-20','Hostel',205), (306,'Overdue',2400.00,'2025-03-01','Mess',206), (307,'Paid',2600.00,'2025-03-05','Mess',207), (308,'Pending',2750.00,'2025-03-15','Mess',208), (309,'Paid',5000.00,'2025-03-25','Hostel',209), (310,'Paid',2350.00,'2025-04-01','Mess',210);

INSERT INTO visitor VALUES
('Ajay Verma','8000123456','Brother','2025-09-15','2025-09-15'), ('Gopal Sharma','9123456780','Father','2025-09-10','2025-09-10'), ('Kavita Patil','7012987654','Sister','2025-09-18','2025-09-18'), ('Manish Singh','9444333222','Father','2025-10-05','2025-10-05'), ('Neha Deshmukh','8111222333','Sister','2025-10-08','2025-10-08'), ('Nikhil Nair','9234567890','Cousin','2025-09-28','2025-09-29'), ('Pooja Gupta','9988776655','Friend','2025-09-25','2025-09-25'), ('Preeti Iyer','7778889990','Mother','2025-10-01','2025-10-01'), ('Rajesh Reddy','9555444333','Uncle','2025-09-22','2025-09-22'), ('Sunita Menon','9876543211','Mother','2025-09-11','2025-09-12');

INSERT INTO visitedby VALUES
('Gopal Sharma',201), ('Sunita Menon',202), ('Ajay Verma',203), ('Kavita Patil',204), ('Neha Deshmukh',204), ('Rajesh Reddy',205), ('Pooja Gupta',206), ('Nikhil Nair',207), ('Preeti Iyer',208), ('Manish Singh',209);

INSERT INTO studentphone VALUES
('8123456789',201),('9876543210',201), ('9000111222',202),('9998887776',202), ('9012301234',205),('7000700070',206), ('9900990099',207),('9517538520',208), ('7654321098',210),('8888877777',210);

INSERT INTO roomallocation VALUES
('2024-07-01','2025-06-30',201,2), ('2025-10-10',NULL,201,5), ('2025-08-19',NULL,201,6), ('2024-07-01','2025-06-30',202,2), ('2024-07-01','2025-06-30',203,7), ('2024-07-01','2025-06-30',204,1), ('2024-07-01','2025-06-30',205,3), ('2024-07-01','2025-06-30',206,7), ('2024-07-01','2025-06-30',207,8), ('2024-07-01','2025-06-30',208,9), ('2025-06-30',NULL,209,1), ('2024-07-01','2025-06-30',209,10), ('2025-01-01','2025-06-30',210,3);

-- 4. DATABASE LOGIC (TRIGGER, FUNCTION, PROCEDURE)

DELIMITER ;;

-- TRIGGER: before_room_allocation_insert (Capacity Check)
CREATE TRIGGER before_room_allocation_insert
BEFORE INSERT ON roomallocation
FOR EACH ROW
BEGIN
    DECLARE current_occupancy INT DEFAULT 0;
    DECLARE room_capacity INT DEFAULT 0;

    SELECT COUNT(*) INTO current_occupancy
    FROM RoomAllocation
    WHERE Room_ID = NEW.Room_ID
      AND VacateDate IS NULL;

    SELECT Capacity INTO room_capacity
    FROM ROOM
    WHERE Room_ID = NEW.Room_ID;

    IF room_capacity IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Room does not exist.';
    END IF;

    IF current_occupancy >= room_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Room capacity reached. Cannot allocate more students.';
    END IF;
END ;;

-- FUNCTION: CalculatePendingFees
CREATE FUNCTION CalculatePendingFees(student_id_in INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE total_pending DECIMAL(10, 2);
    SELECT SUM(FeesAmount) INTO total_pending
    FROM Fees
    WHERE Student_ID = student_id_in
      AND Status IN ('Pending', 'Overdue');

    IF total_pending IS NULL THEN
        RETURN 0.00;
    ELSE
        RETURN total_pending;
    END IF;
END ;;

-- PROCEDURE: HandleRoomAllocation
CREATE PROCEDURE HandleRoomAllocation(
    IN student_id_in INT,
    IN new_room_id_in INT,
    IN allocation_date_in DATE
)
BEGIN
    DECLARE old_room_id_var INT DEFAULT NULL;
    DECLARE old_room_occupancy INT DEFAULT 0;

    SELECT Room_ID INTO old_room_id_var
    FROM STUDENT
    WHERE Student_ID = student_id_in
    LIMIT 1;

    START TRANSACTION;

    IF old_room_id_var IS NOT NULL AND old_room_id_var <> new_room_id_in THEN
        UPDATE RoomAllocation
        SET VacateDate = allocation_date_in
        WHERE Student_ID = student_id_in
          AND VacateDate IS NULL;

        SELECT COUNT(*) INTO old_room_occupancy
        FROM RoomAllocation
        WHERE Room_ID = old_room_id_var
          AND VacateDate IS NULL;

        IF old_room_occupancy = 0 THEN
            UPDATE ROOM
            SET Status = 'Available'
            WHERE Room_ID = old_room_id_var;
        END IF;
    END IF;

    INSERT INTO RoomAllocation (AllocationDate, Student_ID, Room_ID)
    VALUES (allocation_date_in, student_id_in, new_room_id_in);

    UPDATE STUDENT
    SET Room_ID = new_room_id_in
    WHERE Student_ID = student_id_in;

    UPDATE ROOM
    SET Status = 'Occupied'
    WHERE Room_ID = new_room_id_in;

    COMMIT;
END ;;
DELIMITER ;