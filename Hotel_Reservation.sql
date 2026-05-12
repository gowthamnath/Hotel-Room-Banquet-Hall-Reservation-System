
# Hotel Room and Banquet Hall Reservation System - Database Schema

# SECTION 1: DROP EXISTING TABLES (if they exist)

# Drop child tables first, then parent tables to avoid foreign key constraint errors

DROP TABLE IF EXISTS Booking;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS User;


# SECTION 2: CREATE TABLES

# Table: User
# Purpose: Central authentication and profile table for all user types
# Combines: Guest, Staff, and Admin into a single unified table
# Role-based design: Guest-specific and Staff-specific fields allow NULL
# -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    role ENUM('Guest', 'Staff', 'Admin') NOT NULL,
    
    # Guest-specific fields (NULL for Staff/Admin)
    id_proof_type VARCHAR(50),
    id_proof_number VARCHAR(50),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    
    # Staff-specific fields (NULL for Guest)
    employee_id VARCHAR(20) UNIQUE,
    position VARCHAR(50),
    department VARCHAR(50),
    hire_date DATE,
    security_question_1 VARCHAR(255),
    security_answer_1_hash VARCHAR(255),
    security_question_2 VARCHAR(255),
    security_answer_2_hash VARCHAR(255),
    
    
    # Audit and status fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    # Constraints
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_employee_id (employee_id),
    INDEX idx_security_q1 (security_question_1),
    INDEX idx_security_q2 (security_question_2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


# Table: Room
# Purpose: Unified table for both hotel rooms and banquet halls
# Dual-purpose design: is_banquet_hall flag distinguishes between types
# Pricing: price_per_night for rooms, price_per_hour for halls

CREATE TABLE IF NOT EXISTS Room (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type ENUM('Single', 'Double', 'Suite', 'Deluxe', 'Executive', 'Family', 'Presidential', 'Hall-50', 'Hall-150', 'Hall-300') NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    
    # Room-specific fields (NULL for banquet halls)
    price_per_night DECIMAL(10,2),
    floor INT,
    
    # Banquet hall-specific fields (NULL for rooms)
    hall_name VARCHAR(100),
    is_banquet_hall BOOLEAN DEFAULT FALSE,
    price_per_hour DECIMAL(10,2),
    location VARCHAR(100),
    
    # Common fields
    status ENUM('Available', 'Occupied', 'Reserved', 'Maintenance') NOT NULL DEFAULT 'Available',
    amenities TEXT,
    
    # Constraints
    INDEX idx_room_number (room_number),
    INDEX idx_room_type (room_type),
    INDEX idx_is_banquet_hall (is_banquet_hall),
    INDEX idx_status (status),
    
    # Business logic constraints
    CHECK ((is_banquet_hall = FALSE AND price_per_night IS NOT NULL) OR (is_banquet_hall = TRUE AND price_per_hour IS NOT NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

# Table: Reservation
# Purpose: Room reservation records with integrated payment and check-in tracking
# Includes: Guest booking details, payment info, and check-in/out timestamps

CREATE TABLE IF NOT EXISTS Reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    staff_id INT,
    
    # Reservation details
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    num_guests INT NOT NULL CHECK (num_guests > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    
    # Integrated payment tracking
    payment_status ENUM('Pending', 'Completed', 'Failed', 'Refunded', 'Refund requested'),
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'Zelle', 'Net Banking'),
    transaction_id VARCHAR(100),
    payment_date DATETIME,
    
    # Integrated check-in/out tracking
    actual_checkin DATETIME,
    actual_checkout DATETIME,
    
    # Status and metadata
    status ENUM('Pending', 'Confirmed', 'Checked-In', 'Checked-Out', 'Cancelled', 'Completed') NOT NULL DEFAULT 'Pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    special_requests TEXT,
    
    # Foreign key constraints
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES User(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    # Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_room_id (room_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_check_in_date (check_in_date),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status),
    
    # Business logic constraints
    CHECK (check_out_date > check_in_date),
    CHECK ((actual_checkout IS NULL) OR (actual_checkout >= actual_checkin))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

# Table: Booking
# Purpose: Banquet hall bookings with integrated payment and service tracking
# Includes: Event details, payment info, and embedded service requests

CREATE TABLE IF NOT EXISTS Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    staff_id INT,
    
    # Event details
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    guest_count INT NOT NULL CHECK (guest_count > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    
    # Integrated payment tracking
    payment_status ENUM('Pending', 'Completed', 'Failed', 'Refunded', 'Refund requested'),
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'Zelle', 'Net Banking'),
    transaction_id VARCHAR(100),
    payment_date DATETIME,
    
    # Status and metadata
    status ENUM('Pending', 'Confirmed', 'In Progress', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    # Foreign key constraints
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES User(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    # Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_room_id (room_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_event_date (event_date),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status),
    
    # Business logic constraints
    CHECK (end_time > start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


# SECTION 3: INSERT SAMPLE DATA

# Professional, realistic sample data for all tables
# 30+ records per table as required
# Insert Users (40 records: 25 Guests, 10 Staff, 5 Admins)
# Password hash represents: hashed 'password123' (in production, use proper bcrypt/PBKDF2)

# Guests (25 records)
INSERT INTO User (username, password_hash, email, first_name, last_name, phone, role, id_proof_type, id_proof_number, address, city, country, security_question_1, security_answer_1_hash, security_question_2, security_answer_2_hash ) VALUES
('jsmith', '$2y$10$yourGeneratedHashHere', 'john.smith@email.com', 'John', 'Smith', '+1-555-0101', 'Guest', 'Passport', 'P12345678', '123 Oak Street', 'New York', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('mjohnson', '$2y$10$yourGeneratedHashHere', 'mary.johnson@email.com', 'Mary', 'Johnson', '+1-555-0102', 'Guest', 'Driver License', 'DL987654', '456 Maple Avenue', 'Los Angeles', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('rwilliams', '$2y$10$yourGeneratedHashHere', 'robert.williams@email.com', 'Robert', 'Williams', '+1-555-0103', 'Guest', 'Passport', 'P23456789', '789 Pine Road', 'Chicago', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('pbrown', '$2y$10$yourGeneratedHashHere', 'patricia.brown@email.com', 'Patricia', 'Brown', '+1-555-0104', 'Guest', 'Passport', 'P34567890', '321 Elm Street', 'Houston', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('mjones', '$2y$10$yourGeneratedHashHere', 'michael.jones@email.com', 'Michael', 'Jones', '+1-555-0105', 'Guest', 'Driver License', 'DL876543', '654 Birch Lane', 'Phoenix', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('lgarcía', '$2y$10$yourGeneratedHashHere', 'linda.garcia@email.com', 'Linda', 'García', '+1-555-0106', 'Guest', 'Passport', 'P45678901', '987 Cedar Court', 'Philadelphia', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('dmiller', '$2y$10$yourGeneratedHashHere', 'david.miller@email.com', 'David', 'Miller', '+1-555-0107', 'Guest', 'Passport', 'P56789012', '147 Spruce Way', 'San Antonio', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('bdavis', '$2y$10$yourGeneratedHashHere', 'barbara.davis@email.com', 'Barbara', 'Davis', '+1-555-0108', 'Guest', 'Driver License', 'DL765432', '258 Willow Drive', 'San Diego', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('rrodriguez', '$2y$10$yourGeneratedHashHere', 'richard.rodriguez@email.com', 'Richard', 'Rodriguez', '+1-555-0109', 'Guest', 'Passport', 'P67890123', '369 Ash Boulevard', 'Dallas', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('swilson', '$2y$10$yourGeneratedHashHere', 'susan.wilson@email.com', 'Susan', 'Wilson', '+1-555-0110', 'Guest', 'Passport', 'P78901234', '741 Poplar Place', 'San Jose', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('jmartinez', '$2y$10$yourGeneratedHashHere', 'james.martinez@email.com', 'James', 'Martinez', '+1-555-0111', 'Guest', 'Driver License', 'DL654321', '852 Hickory Street', 'Austin', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('kanderson', '$2y$10$yourGeneratedHashHere', 'karen.anderson@email.com', 'Karen', 'Anderson', '+1-555-0112', 'Guest', 'Passport', 'P89012345', '963 Walnut Avenue', 'Jacksonville', 'USA','What was the name of your first pet?','Buddy', 'In what city were you born?', 'New York'),
('ctaylor', '$2y$10$yourGeneratedHashHere', 'charles.taylor@email.com', 'Charles', 'Taylor', '+1-555-0113', 'Guest', 'Passport', 'P90123456', '159 Chestnut Road', 'Fort Worth', 'USA','What was the name of your first pet?','Lovely', 'In what city were you born?', 'New Jersey'),
('nthomas', '$2y$10$yourGeneratedHashHere', 'nancy.thomas@email.com', 'Nancy', 'Thomas', '+1-555-0114', 'Guest', 'Driver License', 'DL543210', '357 Beech Lane', 'Columbus', 'USA','What was the name of your first pet?','Lucky', 'In what city were you born?', 'Detroit'),
('dhernandez', '$2y$10$yourGeneratedHashHere', 'daniel.hernandez@email.com', 'Daniel', 'Hernandez', '+1-555-0115', 'Guest', 'Passport', 'P01234567', '426 Sycamore Court', 'Charlotte', 'USA','What was the name of your first pet?','Kent', 'In what city were you born?', 'Toledo'),
('bmoore', '$2y$10$yourGeneratedHashHere', 'betty.moore@email.com', 'Betty', 'Moore', '+1-555-0116', 'Guest', 'Passport', 'P11234568', '537 Magnolia Way', 'San Francisco', 'USA','What was the name of your first pet?','Lucifer', 'In what city were you born?', 'Baltimore'),
('pmartin', '$2y$10$yourGeneratedHashHere', 'paul.martin@email.com', 'Paul', 'Martin', '+1-555-0117', 'Guest', 'Driver License', 'DL432109', '648 Dogwood Drive', 'Indianapolis', 'USA','What was the name of your first pet?','Justin', 'In what city were you born?', 'Springfield'),
('djackson', '$2y$10$yourGeneratedHashHere', 'dorothy.jackson@email.com', 'Dorothy', 'Jackson', '+1-555-0118', 'Guest', 'Passport', 'P22345679', '759 Redwood Boulevard', 'Seattle', 'USA','What was the name of your first pet?','Honey', 'In what city were you born?', 'Midland'),
('mthompson', '$2y$10$yourGeneratedHashHere', 'mark.thompson@email.com', 'Mark', 'Thompson', '+1-555-0119', 'Guest', 'Passport', 'P33456780', '861 Sequoia Place', 'Denver', 'USA','What was the name of your first pet?','Tim', 'In what city were you born?', 'Saginaw'),
('lwhite', '$2y$10$yourGeneratedHashHere', 'lisa.white@email.com', 'Lisa', 'White', '+1-555-0120', 'Guest', 'Driver License', 'DL321098', '972 Fir Street', 'Boston', 'USA','What was the name of your first pet?','Venie', 'In what city were you born?', 'Midland'),
('gharris', '$2y$10$yourGeneratedHashHere', 'george.harris@email.com', 'George', 'Harris', '+1-555-0121', 'Guest', 'Passport', 'P44567891', '183 Cypress Avenue', 'Nashville', 'USA','What was the name of your first pet?','Daisy', 'In what city were you born?', 'Lansing'),
('hclark', '$2y$10$yourGeneratedHashHere', 'helen.clark@email.com', 'Helen', 'Clark', '+1-555-0122', 'Guest', 'Passport', 'P55678902', '294 Juniper Road', 'Detroit', 'USA','What was the name of your first pet?','Rhyme', 'In what city were you born?', 'Boston'),
('slewis', '$2y$10$yourGeneratedHashHere', 'steven.lewis@email.com', 'Steven', 'Lewis', '+1-555-0123', 'Guest', 'Driver License', 'DL210987', '405 Cedar Lane', 'Portland', 'USA','What was the name of your first pet?','Brownie', 'In what city were you born?', 'Dallas'),
('mrobinson', '$2y$10$yourGeneratedHashHere', 'margaret.robinson@email.com', 'Margaret', 'Robinson', '+1-555-0124', 'Guest', 'Passport', 'P66789013', '516 Laurel Court', 'Las Vegas', 'USA','What was the name of your first pet?','Tom', 'In what city were you born?', 'Chicago'),
('ewalker', '$2y$10$yourGeneratedHashHere', 'edward.walker@email.com', 'Edward', 'Walker', '+1-555-0125', 'Guest', 'Passport', 'P77890124', '627 Alder Way', 'Memphis', 'USA','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit');

# Staff (10 records)
INSERT INTO User (username, password_hash, email, first_name, last_name, phone, role, employee_id, position, department, hire_date, security_question_1, security_answer_1_hash, security_question_2, security_answer_2_hash) VALUES
('aramirez', '$2y$10$yourGeneratedHashHere', 'amanda.ramirez@hotel.com', 'Amanda', 'Ramirez', '+1-555-0201', 'Staff', 'EMP001', 'Front Desk Manager', 'Reception', '2020-03-15','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit' ),
('bking', '$2y$10$yourGeneratedHashHere', 'brian.king@hotel.com', 'Brian', 'King', '+1-555-0202', 'Staff', 'EMP002', 'Reservations Specialist', 'Bookings', '2021-06-01','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('cscott', '$2y$10$yourGeneratedHashHere', 'christine.scott@hotel.com', 'Christine', 'Scott', '+1-555-0203', 'Staff', 'EMP003', 'Event Coordinator', 'Events', '2019-09-20','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('dgreen', '$2y$10$yourGeneratedHashHere', 'daniel.green@hotel.com', 'Daniel', 'Green', '+1-555-0204', 'Staff', 'EMP004', 'Guest Services Agent', 'Reception', '2022-01-10','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('eadams', '$2y$10$yourGeneratedHashHere', 'emily.adams@hotel.com', 'Emily', 'Adams', '+1-555-0205', 'Staff', 'EMP005', 'Banquet Manager', 'Events', '2020-11-05','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('fbaker', '$2y$10$yourGeneratedHashHere', 'frank.baker@hotel.com', 'Frank', 'Baker', '+1-555-0206', 'Staff', 'EMP006', 'Concierge', 'Guest Services', '2021-04-12','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('gnelson', '$2y$10$yourGeneratedHashHere', 'grace.nelson@hotel.com', 'Grace', 'Nelson', '+1-555-0207', 'Staff', 'EMP007', 'Reservations Agent', 'Bookings', '2022-07-18','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('hcarter', '$2y$10$yourGeneratedHashHere', 'henry.carter@hotel.com', 'Henry', 'Carter', '+1-555-0208', 'Staff', 'EMP008', 'Event Specialist', 'Events', '2020-08-22','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('imtchell', '$2y$10$yourGeneratedHashHere', 'isabel.mitchell@hotel.com', 'Isabel', 'Mitchell', '+1-555-0209', 'Staff', 'EMP009', 'Front Desk Supervisor', 'Reception', '2019-12-03','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('jperez', '$2y$10$yourGeneratedHashHere', 'jose.perez@hotel.com', 'Jose', 'Perez', '+1-555-0210', 'Staff', 'EMP010', 'Guest Relations Manager', 'Guest Services', '2021-02-28','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit');


# Admins (5 records)
INSERT INTO User (username, password_hash, email, first_name,last_name, phone, role, employee_id, position, department, hire_date, security_question_1, security_answer_1_hash, security_question_2, security_answer_2_hash) VALUES
('droberts', '$2y$10$yourGeneratedHashHere', 'david.roberts@hotel.com', 'David', 'Roberts', '+1-555-0301', 'Admin', 'ADM001', 'General Manager', 'Administration', '2018-01-15','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('sturner', '$2y$10$yourGeneratedHashHere', 'sarah.turner@hotel.com', 'Sarah', 'Turner', '+1-555-0302', 'Admin', 'ADM002', 'Operations Director', 'Operations', '2018-05-20','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('mphillips', '$2y$10$yourGeneratedHashHere', 'michael.phillips@hotel.com', 'Michael', 'Phillips', '+1-555-0303', 'Admin', 'ADM003', 'IT Administrator', 'Technology', '2019-03-10','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('jcampbell', '$2y$10$yourGeneratedHashHere', 'jennifer.campbell@hotel.com', 'Jennifer', 'Campbell', '+1-555-0304', 'Admin', 'ADM004', 'Finance Manager', 'Finance', '2018-09-01','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit'),
('wparker', '1$2y$10$yourGeneratedHashHere', 'william.parker@hotel.com', 'William', 'Parker', '+1-555-0305', 'Admin', 'ADM005', 'Human Resources Director', 'HR', '2019-07-15','What was the name of your first pet?','Chocolate', 'In what city were you born?', 'Detroit');


# Insert Rooms (35 records: 25 Hotel Rooms + 10 Banquet Halls)

# Hotel Rooms (25 records)
INSERT INTO Room (room_number, room_type, capacity, price_per_night, floor, is_banquet_hall, status, amenities) VALUES
('101', 'Single', 1, 89.00, 1, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Coffee Maker'),
('102', 'Single', 1, 89.00, 1, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Coffee Maker'),
('103', 'Double', 2, 129.00, 1, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Mini Bar, City View'),
('104', 'Double', 2, 129.00, 1, FALSE, 'Occupied', 'Free WiFi, Air Conditioning, TV, Mini Bar, City View'),
('105', 'Suite', 2, 249.00, 1, FALSE, 'Available', 'Free WiFi, Living Area, King Bed, Premium Amenities, Ocean View'),
('201', 'Single', 1, 89.00, 2, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Coffee Maker, Garden View'),
('202', 'Double', 2, 135.00, 2, FALSE, 'Reserved', 'Free WiFi, Air Conditioning, TV, Mini Bar, Balcony'),
('203', 'Double', 2, 135.00, 2, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Mini Bar, Balcony'),
('204', 'Deluxe', 2, 189.00, 2, FALSE, 'Available', 'Free WiFi, King Bed, Premium Toiletries, City View, Work Desk'),
('205', 'Deluxe', 2, 189.00, 2, FALSE, 'Occupied', 'Free WiFi, King Bed, Premium Toiletries, City View, Work Desk'),
('301', 'Suite', 2, 269.00, 3, FALSE, 'Available', 'Free WiFi, Living Area, King Bed, Premium Amenities, Ocean View, Jacuzzi'),
('302', 'Executive', 2, 299.00, 3, FALSE, 'Available', 'Free WiFi, Office Space, Business Amenities, Premium Services'),
('303', 'Executive', 2, 299.00, 3, FALSE, 'Reserved', 'Free WiFi, Office Space, Business Amenities, Premium Services'),
('304', 'Family', 4, 189.00, 3, FALSE, 'Available', 'Free WiFi, 2 Queen + 1 Single Bed, Extra Space, Kid Friendly, Pool Access'),
('305', 'Family', 4, 189.00, 3, FALSE, 'Available', 'Free WiFi, 2 Queen + 1 Single Bed, Extra Space, Kid Friendly, Pool Access'),
('401', 'Deluxe', 2, 199.00, 4, FALSE, 'Available', 'Free WiFi, King Bed, Premium Toiletries, Ocean View, Smart TV'),
('402', 'Suite', 2, 279.00, 4, FALSE, 'Maintenance', 'Free WiFi, Living Area, King Bed, Premium Amenities, Ocean View, Balcony'),
('403', 'Executive', 2, 309.00, 4, FALSE, 'Available', 'Free WiFi, Office Space, Business Amenities, Premium Services, Conference Call Setup'),
('404', 'Family', 4, 199.00, 4, FALSE, 'Occupied', 'Free WiFi, 2 Queen + 1 Single Bed, Extra Space, Kid Friendly, Game Console'),
('405', 'Double', 2, 145.00, 4, FALSE, 'Available', 'Free WiFi, Air Conditioning, TV, Mini Bar, Premium Bedding'),
('501', 'Presidential', 4, 599.00, 5, FALSE, 'Available', '2 King Beds, 2 Bathrooms, Private Terrace, Luxury Amenities, Butler Service, Ocean View'),
('502', 'Presidential', 4, 599.00, 5, FALSE, 'Reserved', '2 King Beds, 2 Bathrooms, Private Terrace, Luxury Amenities, Butler Service, City View'),
('503', 'Suite', 2, 289.00, 5, FALSE, 'Available', 'Free WiFi, Living Area, King Bed, Premium Amenities, Panoramic View, Jacuzzi'),
('504', 'Executive', 2, 319.00, 5, FALSE, 'Available', 'Free WiFi, Office Space, Business Amenities, Premium Services, Private Lounge Access'),
('505', 'Deluxe', 2, 209.00, 5, FALSE, 'Available', 'Free WiFi, King Bed, Premium Toiletries, Panoramic View, Smart Home Controls');

# Banquet Halls (10 records)
INSERT INTO Room (room_number, room_type, capacity, hall_name, is_banquet_hall, price_per_hour, location, status, amenities) VALUES
('BH-01', 'Hall-300', 300, 'Grand Ballroom', TRUE, 500.00, 'Towers 1', 'Available', '5000 sq ft, State-of-the-art AV system, Elegant chandeliers, Professional catering, Dedicated event coordinator'),
('BH-02', 'Hall-150', 150, 'Crystal Hall', TRUE, 300.00, 'Towers 1', 'Available', '2500 sq ft, Natural lighting, Modern decor, In-house catering, Customizable setup'),
('BH-03', 'Hall-50', 50, 'Garden Pavilion', TRUE, 150.00, 'Towers 1', 'Available', 'Outdoor setting, Garden views, Weather-protected, Intimate atmosphere, Perfect for small events'),
('BH-04', 'Hall-150', 100, 'Executive Conference Center', TRUE, 250.00, 'Towers 2', 'Available', 'Business-focused, Advanced technology, Video conferencing, Breakout rooms, Coffee & snacks included'),
('BH-05', 'Hall-300', 250, 'Royal Banquet Hall', TRUE, 450.00, 'Towers 2', 'Reserved', '4500 sq ft, Luxury decor, Grand entrance, Premium catering, Valet parking'),
('BH-06', 'Hall-150', 120, 'Emerald Room', TRUE, 280.00, 'Towers 2', 'Available', '2200 sq ft, Contemporary design, Floor-to-ceiling windows, Built-in bar, Dance floor'),
('BH-07', 'Hall-50', 75, 'Sapphire Lounge', TRUE, 175.00, 'Towers 3', 'Available', 'Elegant setting, Private entrance, City views, Cocktail setup, DJ booth'),
('BH-08', 'Hall-300', 350, 'Diamond Ballroom', TRUE, 550.00, 'Towers 3', 'Available', '6000 sq ft, Luxurious decor, Premium AV equipment, Multiple catering options, Bridal suite'),
('BH-09', 'Hall-150', 180, 'Pearl Hall', TRUE, 320.00, 'Towers 3', 'Maintenance', '3000 sq ft, Garden access, Outdoor terrace, Flexible seating, Natural light'),
('BH-10', 'Hall-50', 60, 'Ruby Meeting Room', TRUE, 160.00, 'Towers 4', 'Available', 'Professional setting, Boardroom style, Video conferencing, Whiteboard, Refreshments included');


# Insert Reservations (35 records with various statuses and dates)

INSERT INTO Reservation (user_id, room_id, staff_id, check_in_date, check_out_date, num_guests, total_amount, payment_status, payment_method, transaction_id, payment_date, actual_checkin, actual_checkout, status, special_requests) VALUES
# Completed reservations
(1, 1, 26, '2025-01-15', '2025-01-18', 1, 267.00, 'Completed', 'Credit Card', 'TXN2025011501', '2025-01-14 10:30:00', '2025-01-15 14:00:00', '2025-01-18 11:00:00', 'Completed', 'Late check-in requested'),
(2, 3, 27, '2025-01-20', '2025-01-23', 2, 387.00, 'Completed', 'Debit Card', 'TXN2025012001', '2025-01-19 15:45:00', '2025-01-20 15:30:00', '2025-01-23 10:30:00', 'Completed', 'Non-smoking room preferred'),
(3, 5, 26, '2025-01-25', '2025-01-30', 2, 1245.00, 'Completed', 'Credit Card', 'TXN2025012501', '2025-01-24 09:15:00', '2025-01-25 16:00:00', '2025-01-30 11:00:00', 'Completed', 'Champagne on arrival'),
(4, 10, 28, '2025-02-01', '2025-02-03', 2, 378.00, 'Completed', 'Cash', NULL, '2025-02-01 14:00:00', '2025-02-01 14:30:00', '2025-02-03 10:00:00', 'Completed', NULL),
(5, 14, 27, '2025-02-05', '2025-02-08', 4, 567.00, 'Completed', 'Credit Card', 'TXN2025020501', '2025-02-04 11:20:00', '2025-02-05 15:00:00', '2025-02-08 11:00:00', 'Completed', 'Connecting rooms if possible'),

# Currently checked-in reservations
(6, 4, 29, '2025-03-01', '2025-03-05', 2, 516.00, 'Completed', 'Credit Card', 'TXN2025030101', '2025-02-28 16:30:00', '2025-03-01 15:00:00', NULL, 'Checked-In', 'Extra towels needed'),
(7, 10, 26, '2025-03-02', '2025-03-06', 2, 756.00, 'Completed', 'Debit Card', 'TXN2025030201', '2025-03-01 10:00:00', '2025-03-02 14:00:00', NULL, 'Checked-In', NULL),
(8, 19, 28, '2025-03-03', '2025-03-07', 4, 796.00, 'Completed', 'Credit Card', 'TXN2025030301', '2025-03-02 13:45:00', '2025-03-03 16:30:00', NULL, 'Checked-In', 'High floor preferred'),

# Confirmed future reservations
(9, 2, 27, '2025-03-10', '2025-03-15', 2, 645.00, 'Completed', 'Credit Card', 'TXN2025031001', '2025-03-08 09:00:00', NULL, NULL, 'Confirmed', 'Early check-in if possible'),
(10, 7, 26, '2025-03-12', '2025-03-14', 2, 270.00, 'Completed', 'Zelle', 'UPI2025031201', '2025-03-10 14:30:00', NULL, NULL, 'Confirmed', 'Quiet room requested'),
(11, 13, 29, '2025-03-15', '2025-03-20', 2, 1495.00, 'Completed', 'Credit Card', 'TXN2025031501', '2025-03-13 11:00:00', NULL, NULL, 'Confirmed', 'Airport pickup required'),
(12, 15, 27, '2025-03-18', '2025-03-22', 4, 756.00, 'Completed', 'Net Banking', 'NET2025031801', '2025-03-16 15:20:00', NULL, NULL, 'Confirmed', 'Crib needed for infant'),
(13, 16, 28, '2025-03-20', '2025-03-25', 2, 995.00, 'Completed', 'Credit Card', 'TXN2025032001', '2025-03-18 10:45:00', NULL, NULL, 'Confirmed', NULL),
(14, 18, 26, '2025-03-22', '2025-03-27', 2, 1545.00, 'Completed', 'Debit Card', 'TXN2025032201', '2025-03-20 16:00:00', NULL, NULL, 'Confirmed', 'Business center access needed'),
(15, 20, 27, '2025-03-25', '2025-03-28', 2, 435.00, 'Completed', 'Credit Card', 'TXN2025032501', '2025-03-23 12:30:00', NULL, NULL, 'Confirmed', 'Late checkout requested'),
(16, 21, 29, '2025-04-01', '2025-04-05', 4, 2396.00, 'Completed', 'Credit Card', 'TXN2025040101', '2025-03-30 09:15:00', NULL, NULL, 'Confirmed', 'Honeymoon package'),
(17, 22, 26, '2025-04-05', '2025-04-10', 4, 2995.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', 'VIP services required'),
(18, 23, 28, '2025-04-08', '2025-04-12', 2, 1156.00, 'Completed', 'Zelle', 'UPI2025040801', '2025-04-06 14:00:00', NULL, NULL, 'Confirmed', 'Ocean view preferred'),
(19, 24, 27, '2025-04-10', '2025-04-15', 2, 1595.00, 'Completed', 'Credit Card', 'TXN2025041001', '2025-04-08 11:30:00', NULL, NULL, 'Confirmed', NULL),
(20, 25, 26, '2025-04-12', '2025-04-17', 2, 1045.00, 'Completed', 'Debit Card', 'TXN2025041201', '2025-04-10 16:45:00', NULL, NULL, 'Confirmed', 'Hypoallergenic pillows'),

# Pending reservations
(21, 11, 27, '2025-04-15', '2025-04-20', 2, 1395.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', 'Waiting for payment confirmation'),
(22, 12, 28, '2025-04-18', '2025-04-22', 2, 1196.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', NULL),
(23, 6, 26, '2025-04-20', '2025-04-25', 1, 475.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', 'Corporate booking'),

# Cancelled reservations
(24, 8, 29, '2025-02-10', '2025-02-15', 2, 675.00, 'Refunded', 'Credit Card', 'TXN2025021001', '2025-02-08 10:00:00', NULL, NULL, 'Cancelled', 'Emergency cancellation'),
(25, 17, 27, '2025-02-20', '2025-02-24', 2, 1116.00, 'Refunded', 'Debit Card', 'TXN2025022001', '2025-02-18 14:30:00', NULL, NULL, 'Cancelled', 'Change of plans'),

# Additional confirmed reservations for variety
(1, 9, 26, '2025-04-25', '2025-04-28', 2, 567.00, 'Completed', 'Credit Card', 'TXN2025042501', '2025-04-23 09:00:00', NULL, NULL, 'Confirmed', 'Anniversary celebration'),
(2, 15, 28, '2025-05-01', '2025-05-05', 4, 756.00, 'Completed', 'Zelle', 'UPI2025050101', '2025-04-29 13:20:00', NULL, NULL, 'Confirmed', 'Family vacation'),
(3, 20, 27, '2025-05-05', '2025-05-08', 2, 435.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', NULL),
(4, 1, 26, '2025-05-10', '2025-05-13', 1, 267.00, 'Completed', 'Net Banking', 'NET2025051001', '2025-05-08 10:15:00', NULL, NULL, 'Confirmed', 'Business trip'),
(5, 3, 29, '2025-05-12', '2025-05-16', 2, 516.00, 'Completed', 'Credit Card', 'TXN2025051201', '2025-05-10 15:30:00', NULL, NULL, 'Confirmed', NULL),
(6, 5, 27, '2025-05-15', '2025-05-20', 2, 1245.00, 'Completed', 'Debit Card', 'TXN2025051501', '2025-05-13 11:45:00', NULL, NULL, 'Confirmed', 'Special occasion package'),
(7, 11, 28, '2025-05-18', '2025-05-23', 2, 1395.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', 'Group booking inquiry'),
(8, 16, 26, '2025-05-20', '2025-05-24', 2, 796.00, 'Completed', 'Credit Card', 'TXN2025052001', '2025-05-18 14:00:00', NULL, NULL, 'Confirmed', 'Mountain view preferred'),
(9, 21, 27, '2025-05-25', '2025-05-30', 4, 2995.00, 'Completed', 'Credit Card', 'TXN2025052501', '2025-05-23 09:30:00', NULL, NULL, 'Confirmed', 'Luxury suite experience'),
(10, 25, 29, '2025-05-28', '2025-06-02', 2, 1045.00, 'Pending', NULL, NULL, NULL, NULL, NULL, 'Pending', 'Awaiting deposit');

# Insert Bookings (30 records for banquet hall events)

INSERT INTO Booking (user_id, room_id, staff_id, event_date, start_time, end_time, event_type, guest_count, total_amount, payment_status, payment_method, transaction_id, payment_date, status) VALUES
-- Completed events
(11, 26, 28, '2025-01-15', '18:00:00', '23:00:00', 'Corporate Gala', 250, 3200.00, 'Completed', 'Credit Card', 'TXN2025011502', '2025-01-10 10:00:00', 'Completed'),
(12, 27, 29, '2025-01-20', '10:00:00', '16:00:00', 'Conference', 120, 2400.00, 'Completed', 'Net Banking', 'NET2025012002', '2025-01-15 14:30:00', 'Completed'),
(13, 28, 28, '2025-01-25', '17:00:00', '22:00:00', 'Birthday Party', 45, 950.00, 'Completed', 'Credit Card', 'TXN2025012502', '2025-01-20 11:15:00', 'Completed'),
(14, 29, 27, '2025-02-01', '09:00:00', '17:00:00', 'Business Meeting', 80, 2800.00, 'Completed', 'Debit Card', 'TXN2025020102', '2025-01-28 09:45:00', 'Completed'),
(15, 30, 28, '2025-02-10', '18:00:00', '23:30:00', 'Wedding Reception', 220, 4250.00, 'Completed', 'Credit Card', 'TXN2025021002', '2025-02-05 16:00:00', 'Completed'),

-- Confirmed upcoming events
(16, 26, 29, '2025-03-15', '19:00:00', '23:59:59', 'Annual Fundraiser', 280, 3800.00, 'Completed', 'Credit Card', 'TXN2025031502', '2025-03-10 10:30:00', 'Confirmed'),
(17, 31, 28, '2025-03-20', '11:00:00', '17:00:00', 'Product Launch', 140, 2650.00, 'Completed', 'Zelle', 'UPI2025032002', '2025-03-15 13:20:00', 'Confirmed'),
(18, 32, 27, '2025-03-25', '18:30:00', '22:00:00', 'Anniversary Celebration', 55, 1100.00, 'Completed', 'Debit Card', 'TXN2025032502', '2025-03-20 15:45:00', 'Confirmed'),
(19, 33, 29, '2025-04-01', '19:00:00', '23:00:00', 'Charity Gala', 320, 5200.00, 'Completed', 'Credit Card', 'TXN2025040102', '2025-03-27 11:00:00', 'Confirmed'),
(20, 28, 28, '2025-04-05', '14:00:00', '18:00:00', 'Baby Shower', 40, 850.00, 'Completed', 'Cash', NULL, '2025-04-01 14:00:00', 'Confirmed'),
(21, 29, 27, '2025-04-10', '08:00:00', '18:00:00', 'Training Seminar', 95, 3100.00, 'Completed', 'Net Banking', 'NET2025041002', '2025-04-05 09:30:00', 'Confirmed'),
(22, 26, 28, '2025-04-15', '18:00:00', '23:00:00', 'Corporate Event', 240, 3500.00, 'Completed', 'Credit Card', 'TXN2025041502', '2025-04-10 10:15:00', 'Confirmed'),
(23, 27, 29, '2025-04-20', '10:00:00', '15:00:00', 'Workshop', 110, 2200.00, 'Completed', 'Zelle', 'UPI2025042002', '2025-04-15 14:45:00', 'Confirmed'),
(24, 30, 27, '2025-04-25', '19:00:00', '23:59:59', 'Wedding Reception', 200, 4000.00, 'Completed', 'Credit Card', 'TXN2025042502', '2025-04-20 10:00:00', 'Confirmed'),
(25, 32, 28, '2025-05-01', '17:00:00', '21:00:00', 'Graduation Party', 70, 1400.00, 'Completed', 'Debit Card', 'TXN2025050102', '2025-04-26 11:00:00', 'Confirmed'),
(26, 32, 28, '2025-05-02', '17:00:00', '21:00:00', 'Graduation Party', 70, 1400.00, 'Completed', 'Debit Card', 'TXN2025050103', '2025-04-26 11:00:00', 'Confirmed'),
(27, 32, 28, '2025-05-03', '17:00:00', '21:00:00', 'Graduation Party', 70, 1400.00, 'Completed', 'Debit Card', 'TXN2025050104', '2025-04-26 11:00:00', 'Confirmed'),

-- In Progress event
(4, 33, 29, '2025-03-08', '14:00:00', '22:00:00', 'Awards Ceremony', 300, 4800.00, 'Completed', 'Credit Card', 'TXN2025030802', '2025-03-03 09:00:00', 'In Progress'),

-- Cancelled events
(5, 27, 28, '2025-02-15', '10:00:00', '16:00:00', 'Conference', 100, 2100.00, 'Refunded', 'Credit Card', 'TXN2025021502', '2025-02-10 14:00:00', 'Cancelled'),
(6, 28, 27, '2025-02-20', '18:00:00', '22:00:00', 'Birthday Party', 40, 850.00, 'Refunded', 'Zelle', 'UPI2025022002', '2025-02-15 11:30:00', 'Cancelled'),

-- Additional confirmed events for variety
(7, 26, 28, '2025-05-20', '19:00:00', '23:30:00', 'Corporate Dinner', 260, 3600.00, 'Completed', 'Net Banking', 'NET2025052002', '2025-05-15 10:00:00', 'Confirmed'),
(8, 30, 29, '2025-05-25', '18:00:00', '23:00:00', 'Wedding Reception', 210, 4100.00, 'Completed', 'Credit Card', 'TXN2025052502', '2025-05-20 15:20:00', 'Confirmed'),
(9, 31, 27, '2025-05-28', '09:00:00', '17:00:00', 'Summit', 150, 2850.00, 'Completed', 'Debit Card', 'TXN2025052802', '2025-05-23 09:45:00', 'Confirmed'),
(10, 32, 28, '2025-06-01', '17:00:00', '22:00:00', 'Alumni Reunion', 65, 1350.00, 'Pending', NULL, NULL, NULL, 'Pending'),
(11, 33, 29, '2025-06-05', '19:00:00', '23:59:59', 'Gala Dinner', 310, 5100.00, 'Completed', 'Credit Card', 'TXN2025060502', '2025-05-30 11:30:00', 'Confirmed'),
(12, 26, 27, '2025-06-10', '18:00:00', '22:00:00', 'Networking Event', 180, 2900.00, 'Pending', NULL, NULL, NULL, 'Pending'),
(13, 29, 28, '2025-06-15', '10:00:00', '16:00:00', 'AGM', 90, 2600.00, 'Completed', 'Zelle', 'UPI2025061502', '2025-06-10 14:00:00', 'Confirmed');


SELECT * FROM User;

