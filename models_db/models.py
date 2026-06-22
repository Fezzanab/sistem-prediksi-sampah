from datetime import datetime
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default="Administrator")
    region = db.Column(db.String(100), default="Kota Bandung")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class District(db.Model):
    __tablename__ = 'districts'
    
    id = db.Column(db.String(50), primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kecamatan = db.Column(db.String(100), nullable=False)
    populasi = db.Column(db.Integer, nullable=False)
    luas_wilayah = db.Column(db.Float, nullable=False)
    kepadatan_penduduk = db.Column(db.Float, nullable=False)
    pendapatan = db.Column(db.Float, nullable=False)
    wisatawan = db.Column(db.Integer, nullable=False)
    
    # Relationships
    horeca_relations = db.relationship('Horeca', backref='district', cascade='all, delete-orphan', lazy=True)
    iot_devices = db.relationship('IoTDevice', backref='district', cascade='all, delete-orphan', lazy=True)
    predictions = db.relationship('PredictionHistory', backref='district', cascade='all, delete-orphan', lazy=True)

    @property
    def total_horeca_waste_index(self):
        """Sum of all Horeca waste indices in this district."""
        return sum(h.waste_index for h in self.horeca_relations)

    @property
    def avg_iot_fill_level(self):
        """Average fill level of all IoT devices in this district."""
        devices = self.iot_devices
        if not devices:
            return 0.0
        return sum(d.fill_level for d in devices) / len(devices)

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "kecamatan": self.kecamatan,
            "populasi": self.populasi,
            "luas_wilayah": self.luas_wilayah,
            "kepadatan_penduduk": self.kepadatan_penduduk,
            "pendapatan": self.pendapatan,
            "wisatawan": self.wisatawan,
            "horeca_index": self.total_horeca_waste_index,
            "iot_index": self.avg_iot_fill_level
        }


class Horeca(db.Model):
    __tablename__ = 'horeca'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.String(50), db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False)
    nama_usaha = db.Column(db.String(150), nullable=False)
    jenis = db.Column(db.String(50), nullable=False) # 'hotel', 'restaurant', 'cafe'
    waste_index = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "district_id": self.district_id,
            "district_name": self.district.nama if self.district else "",
            "nama_usaha": self.nama_usaha,
            "jenis": self.jenis,
            "waste_index": self.waste_index,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }


class IoTDevice(db.Model):
    __tablename__ = 'iot_devices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.String(50), db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False)
    device_code = db.Column(db.String(50), unique=True, nullable=False)
    fill_level = db.Column(db.Float, nullable=False) # percentage (0 - 100)
    volume_m3 = db.Column(db.Float, nullable=False) # current volume
    battery_level = db.Column(db.Float, nullable=False) # battery percentage (0 - 100)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "district_id": self.district_id,
            "district_name": self.district.nama if self.district else "",
            "device_code": self.device_code,
            "fill_level": self.fill_level,
            "volume_m3": self.volume_m3,
            "battery_level": self.battery_level,
            "last_update": self.last_update.strftime("%Y-%m-%d %H:%M:%S") if self.last_update else ""
        }


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.String(50), db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    volume_aktual = db.Column(db.Float, nullable=True) # in tons
    volume_prediksi = db.Column(db.Float, nullable=False) # in tons
    akurasi = db.Column(db.Float, nullable=True) # accuracy percentage vs actual
    model_version = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "district_id": self.district_id,
            "district_name": self.district.nama if self.district else "",
            "tanggal": self.tanggal.strftime("%Y-%m-%d") if self.tanggal else "",
            "volume_aktual": self.volume_aktual,
            "volume_prediksi": self.volume_prediksi,
            "akurasi": self.akurasi,
            "model_version": self.model_version
        }


class ModelRegistry(db.Model):
    __tablename__ = 'model_registry'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    r2_score = db.Column(db.Float, nullable=False)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active') # 'active', 'archive'

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "accuracy": self.accuracy,
            "r2_score": self.r2_score,
            "trained_at": self.trained_at.strftime("%Y-%m-%d %H:%M:%S") if self.trained_at else "",
            "status": self.status
        }
