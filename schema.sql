-- Database setup script for sistem_prediksi_sampah
CREATE DATABASE IF NOT EXISTS sistem_prediksi_sampah;
USE sistem_prediksi_sampah;

-- 1. Districts (Kecamatan) Table
CREATE TABLE IF NOT EXISTS districts (
    id VARCHAR(50) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    kecamatan VARCHAR(100) NOT NULL,
    populasi INT NOT NULL,
    luas_wilayah FLOAT NOT NULL,
    kepadatan_penduduk FLOAT NOT NULL,
    pendapatan FLOAT NOT NULL,
    wisatawan INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Horeca (Hotel, Restaurant, Cafe) Table
CREATE TABLE IF NOT EXISTS horeca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id VARCHAR(50) NOT NULL,
    nama_usaha VARCHAR(150) NOT NULL,
    jenis VARCHAR(50) NOT NULL, -- 'hotel', 'restaurant', 'cafe'
    waste_index FLOAT NOT NULL, -- Waste generation variable
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. IoT Devices Table
CREATE TABLE IF NOT EXISTS iot_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id VARCHAR(50) NOT NULL,
    device_code VARCHAR(50) UNIQUE NOT NULL,
    fill_level FLOAT NOT NULL, -- fill percentage (0 - 100)
    volume_m3 FLOAT NOT NULL, -- volume of waste in cubic meters
    battery_level FLOAT NOT NULL, -- battery percentage (0 - 100)
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Prediction History Table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id VARCHAR(50) NOT NULL,
    tanggal DATE NOT NULL,
    volume_aktual FLOAT NULL, -- Actual waste recorded
    volume_prediksi FLOAT NOT NULL, -- Predicted waste from RF model
    akurasi FLOAT NULL, -- Accuracy percentage vs actual
    model_version VARCHAR(50) NULL,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Model Registry Table
CREATE TABLE IF NOT EXISTS model_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    accuracy FLOAT NOT NULL,
    r2_score FLOAT NOT NULL,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' -- 'active', 'archive'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
