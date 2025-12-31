-- Smart Pet Feeder Database Initialization

USE smart_pet_feeder;

-- Create feeding_history table
CREATE TABLE IF NOT EXISTS feeding_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_weight FLOAT NOT NULL,
    amount FLOAT NOT NULL,
    status_mount VARCHAR(50) NOT NULL,
    motor VARCHAR(10) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_food_weight (food_weight)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some sample data for testing
INSERT INTO feeding_history (food_weight, amount, status_mount, motor, timestamp) VALUES
(50, 2950, '2950', 'close', NOW() - INTERVAL 1 HOUR),
(75, 2875, '2875', 'close', NOW() - INTERVAL 2 HOUR),
(60, 2815, '2815', 'close', NOW() - INTERVAL 3 HOUR),
(45, 2770, '2770', 'close', NOW() - INTERVAL 4 HOUR),
(80, 2690, '2690', 'close', NOW() - INTERVAL 5 HOUR);

-- Grant privileges
GRANT ALL PRIVILEGES ON smart_pet_feeder.* TO 'feeder_user'@'%';
FLUSH PRIVILEGES;
