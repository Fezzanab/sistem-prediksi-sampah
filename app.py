import os
import datetime
import logging
from flask import Flask, session
from config import Config
from models_db.database import db, init_db
from models_db.models import AdminUser, District, Horeca, IoTDevice, PredictionHistory, ModelRegistry
from services.ai_client import AIClient

# Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.data import data_bp
from routes.prediction import prediction_bp
from routes.gis import gis_bp

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Database Layer
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(gis_bp)
    
    # Inject global templates variables
    @app.context_processor
    def inject_global_template_vars():
        ai_online = AIClient.check_health()
        
        # Compile dynamic alerts based on district prediction values
        critical_alerts = []
        try:
            districts = District.query.all()
            for d in districts:
                # Approximate volume estimation
                base_vol = (d.populasi * 0.00015) + (d.luas_wilayah * 0.1)
                horeca_mul = 1.0 + (d.total_horeca_waste_index * 0.05)
                iot_mul = 1.0 + (d.avg_iot_fill_level * 0.002)
                prediksi = round(base_vol * horeca_mul * iot_mul * 1.03, 1)
                
                if prediksi > 15.0:
                    critical_alerts.append({
                        "zona": d.nama,
                        "pesan": f"Volume melebihi kapasitas 118% ({prediksi} ton) &mdash; armada tambahan diperlukan segera.",
                        "level": "overflow",
                        "waktu": "08:14"
                    })
                elif prediksi > 9.0:
                    critical_alerts.append({
                        "zona": d.nama,
                        "pesan": f"Prediksi kritis besok ({prediksi} ton) &mdash; lakukan koordinasi jadwal pengambilan.",
                        "level": "kritis",
                        "waktu": "07:52"
                    })
        except Exception:
            pass # database not seeded yet
            
        return {
            "ai_online": ai_online,
            "critical_alerts": critical_alerts,
            "critical_alerts_count": len(critical_alerts),
            "last_update_time": datetime.datetime.now().strftime("%d %b %Y, %H:%M WIB")
        }
        
    # Auto Seed initial datasets if empty
    with app.app_context():
        try:
            seed_database()
        except Exception as e:
            logging.error(f"Error seeding database: {e}")
            
    return app

def seed_database():
    """Seeds default admin login and waste metrics for 30 Bandung kecamatan districts."""
    # 1. Seed Admin User
    if not AdminUser.query.first():
        admin = AdminUser(
            username="admin",
            name="Administrator DLH Bandung",
            role="Super Admin",
            region="Kota Bandung"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        logging.info("Seeded admin user (username: admin, password: admin123)")

    # 2. Seed 30 Bandung Kecamatan (id matched to GeoJSON id_kecamatan)
    if not District.query.first():
        districts_seed = [
            District(id="3273180", nama="Kec. Andir",              kecamatan="Andir",              populasi=87320, luas_wilayah=3.70, kepadatan_penduduk=23600.0, pendapatan=6500000,  wisatawan=1200),
            District(id="3273141", nama="Kec. Antapani",           kecamatan="Antapani",           populasi=77830, luas_wilayah=3.79, kepadatan_penduduk=20536.0, pendapatan=7800000,  wisatawan=900),
            District(id="3273130", nama="Kec. Arcamanik",          kecamatan="Arcamanik",          populasi=64200, luas_wilayah=5.87, kepadatan_penduduk=10938.0, pendapatan=8200000,  wisatawan=700),
            District(id="3273050", nama="Kec. Astanaanyar",        kecamatan="Astanaanyar",        populasi=66540, luas_wilayah=2.89, kepadatan_penduduk=23025.0, pendapatan=6200000,  wisatawan=1100),
            District(id="3273020", nama="Kec. Babakan Ciparay",    kecamatan="Babakan Ciparay",    populasi=120500, luas_wilayah=6.87, kepadatan_penduduk=17540.0, pendapatan=5800000, wisatawan=600),
            District(id="3273080", nama="Kec. Bandung Kidul",      kecamatan="Bandung Kidul",      populasi=56700, luas_wilayah=6.06, kepadatan_penduduk=9356.0, pendapatan=7500000,  wisatawan=800),
            District(id="3273010", nama="Kec. Bandung Kulon",      kecamatan="Bandung Kulon",      populasi=122400, luas_wilayah=6.46, kepadatan_penduduk=18950.0, pendapatan=5600000, wisatawan=500),
            District(id="3273200", nama="Kec. Bandung Wetan",      kecamatan="Bandung Wetan",      populasi=31200, luas_wilayah=3.39, kepadatan_penduduk=9203.0, pendapatan=11000000, wisatawan=4500),
            District(id="3273160", nama="Kec. Batununggal",        kecamatan="Batununggal",        populasi=88700, luas_wilayah=5.03, kepadatan_penduduk=17634.0, pendapatan=6800000, wisatawan=750),
            District(id="3273030", nama="Kec. Bojongloa Kaler",    kecamatan="Bojongloa Kaler",    populasi=107200, luas_wilayah=3.03, kepadatan_penduduk=35380.0, pendapatan=5500000, wisatawan=450),
            District(id="3273040", nama="Kec. Bojongloa Kidul",    kecamatan="Bojongloa Kidul",    populasi=73600, luas_wilayah=6.26, kepadatan_penduduk=11757.0, pendapatan=5700000, wisatawan=400),
            District(id="3273090", nama="Kec. Buahbatu",           kecamatan="Buahbatu",           populasi=91400, luas_wilayah=7.90, kepadatan_penduduk=11569.0, pendapatan=9500000, wisatawan=1300),
            District(id="3273220", nama="Kec. Cibeunying Kaler",   kecamatan="Cibeunying Kaler",   populasi=68900, luas_wilayah=4.50, kepadatan_penduduk=15311.0, pendapatan=8800000, wisatawan=1600),
            District(id="3273210", nama="Kec. Cibeunying Kidul",   kecamatan="Cibeunying Kidul",   populasi=78300, luas_wilayah=5.25, kepadatan_penduduk=14914.0, pendapatan=8200000, wisatawan=1400),
            District(id="3273110", nama="Kec. Cibiru",             kecamatan="Cibiru",             populasi=62100, luas_wilayah=6.32, kepadatan_penduduk=9826.0, pendapatan=7200000,  wisatawan=600),
            District(id="3273190", nama="Kec. Cicendo",            kecamatan="Cicendo",            populasi=85600, luas_wilayah=6.86, kepadatan_penduduk=12479.0, pendapatan=7600000, wisatawan=900),
            District(id="3273260", nama="Kec. Cidadap",            kecamatan="Cidadap",            populasi=42300, luas_wilayah=6.11, kepadatan_penduduk=6923.0, pendapatan=13000000, wisatawan=2100),
            District(id="3273121", nama="Kec. Cinambo",            kecamatan="Cinambo",            populasi=28700, luas_wilayah=3.68, kepadatan_penduduk=7799.0, pendapatan=7900000,  wisatawan=300),
            District(id="3273230", nama="Kec. Coblong",            kecamatan="Coblong",            populasi=100400, luas_wilayah=7.35, kepadatan_penduduk=13660.0, pendapatan=9800000, wisatawan=5800),
            District(id="3273101", nama="Kec. Gedebage",           kecamatan="Gedebage",           populasi=34500, luas_wilayah=9.58, kepadatan_penduduk=3601.0, pendapatan=8500000,  wisatawan=400),
            District(id="3273150", nama="Kec. Kiaracondong",       kecamatan="Kiaracondong",       populasi=126700, luas_wilayah=6.10, kepadatan_penduduk=20770.0, pendapatan=6100000, wisatawan=800),
            District(id="3273070", nama="Kec. Lengkong",           kecamatan="Lengkong",           populasi=57400, luas_wilayah=5.90, kepadatan_penduduk=9729.0, pendapatan=10200000, wisatawan=2700),
            District(id="3273142", nama="Kec. Mandalajati",        kecamatan="Mandalajati",        populasi=67100, luas_wilayah=6.67, kepadatan_penduduk=10060.0, pendapatan=8600000, wisatawan=600),
            District(id="3273111", nama="Kec. Panyileukan",        kecamatan="Panyileukan",        populasi=48900, luas_wilayah=8.20, kepadatan_penduduk=5963.0, pendapatan=8100000,  wisatawan=350),
            District(id="3273100", nama="Kec. Rancasari",          kecamatan="Rancasari",          populasi=72600, luas_wilayah=7.33, kepadatan_penduduk=9905.0, pendapatan=9100000,  wisatawan=700),
            District(id="3273060", nama="Kec. Regol",              kecamatan="Regol",              populasi=68200, luas_wilayah=4.30, kepadatan_penduduk=15860.0, pendapatan=7400000, wisatawan=1800),
            District(id="3273240", nama="Kec. Sukajadi",           kecamatan="Sukajadi",           populasi=96300, luas_wilayah=4.30, kepadatan_penduduk=22395.0, pendapatan=9200000, wisatawan=3200),
            District(id="3273250", nama="Kec. Sukasari",           kecamatan="Sukasari",           populasi=78100, luas_wilayah=6.33, kepadatan_penduduk=12337.0, pendapatan=12500000, wisatawan=2400),
            District(id="3273170", nama="Kec. Sumur Bandung",      kecamatan="Sumur Bandung",      populasi=34700, luas_wilayah=3.40, kepadatan_penduduk=10206.0, pendapatan=13500000, wisatawan=8200),
            District(id="3273120", nama="Kec. Ujungberung",        kecamatan="Ujungberung",        populasi=78900, luas_wilayah=6.40, kepadatan_penduduk=12328.0, pendapatan=7000000, wisatawan=550),
        ]
        db.session.add_all(districts_seed)
        db.session.commit()
        logging.info("Seeded 30 Bandung kecamatan districts.")
        
        # 3. Seed Horeca (Bandung establishments)
        horeca_seed = [
            Horeca(district_id="3273200", nama_usaha="Hotel Savoy Homann",      jenis="hotel",      waste_index=3.2),
            Horeca(district_id="3273200", nama_usaha="Restoran Braga Permai",    jenis="restaurant", waste_index=1.8),
            Horeca(district_id="3273230", nama_usaha="Hotel Grand Serela",        jenis="hotel",      waste_index=2.9),
            Horeca(district_id="3273230", nama_usaha="Kopi Malabar Coblong",      jenis="cafe",       waste_index=0.6),
            Horeca(district_id="3273230", nama_usaha="Warung Nasi Ampera Dago",   jenis="restaurant", waste_index=1.2),
            Horeca(district_id="3273170", nama_usaha="Hotel Preanger Bandung",    jenis="hotel",      waste_index=4.1),
            Horeca(district_id="3273170", nama_usaha="Cafe Reka Braga",           jenis="cafe",       waste_index=0.55),
            Horeca(district_id="3273240", nama_usaha="Hotel Nalendra Sukajadi",   jenis="hotel",      waste_index=2.5),
            Horeca(district_id="3273240", nama_usaha="Warung Pak Budi Sukajadi",  jenis="restaurant", waste_index=0.9),
            Horeca(district_id="3273150", nama_usaha="Restoran Sari Sunda Kiarac",jenis="restaurant", waste_index=1.6),
            Horeca(district_id="3273030", nama_usaha="Warteg Bojongloa Kaler",    jenis="restaurant", waste_index=1.1),
            Horeca(district_id="3273020", nama_usaha="Cafe Babakan Siliwangi",    jenis="cafe",       waste_index=0.75),
            Horeca(district_id="3273090", nama_usaha="Hotel Aston Priority",      jenis="hotel",      waste_index=3.0),
            Horeca(district_id="3273250", nama_usaha="Hotel Swiss-Belinn",        jenis="hotel",      waste_index=2.7),
            Horeca(district_id="3273260", nama_usaha="Cafe Dago Pakar",           jenis="cafe",       waste_index=0.8),
        ]
        db.session.add_all(horeca_seed)

        # 4. Seed IoT devices across Bandung districts
        iot_seed = [
            IoTDevice(district_id="3273180", device_code="IOT-BDG-AND-01", fill_level=78.0, volume_m3=1.1, battery_level=91.0),
            IoTDevice(district_id="3273141", device_code="IOT-BDG-ANT-01", fill_level=55.0, volume_m3=0.7, battery_level=88.0),
            IoTDevice(district_id="3273130", device_code="IOT-BDG-ARC-01", fill_level=42.0, volume_m3=0.6, battery_level=95.0),
            IoTDevice(district_id="3273050", device_code="IOT-BDG-AST-01", fill_level=82.0, volume_m3=1.2, battery_level=79.0),
            IoTDevice(district_id="3273020", device_code="IOT-BDG-BBC-01", fill_level=91.5, volume_m3=1.6, battery_level=14.0),
            IoTDevice(district_id="3273080", device_code="IOT-BDG-BKI-01", fill_level=38.0, volume_m3=0.5, battery_level=97.0),
            IoTDevice(district_id="3273010", device_code="IOT-BDG-BKU-01", fill_level=88.0, volume_m3=1.4, battery_level=83.0),
            IoTDevice(district_id="3273200", device_code="IOT-BDG-BWE-01", fill_level=61.0, volume_m3=0.8, battery_level=90.0),
            IoTDevice(district_id="3273160", device_code="IOT-BDG-BAT-01", fill_level=74.0, volume_m3=1.0, battery_level=86.0),
            IoTDevice(district_id="3273030", device_code="IOT-BDG-BJK-01", fill_level=95.0, volume_m3=1.9, battery_level=22.0),
            IoTDevice(district_id="3273040", device_code="IOT-BDG-BJD-01", fill_level=66.0, volume_m3=0.9, battery_level=93.0),
            IoTDevice(district_id="3273090", device_code="IOT-BDG-BUA-01", fill_level=49.0, volume_m3=0.7, battery_level=99.0),
            IoTDevice(district_id="3273220", device_code="IOT-BDG-CBK-01", fill_level=58.0, volume_m3=0.8, battery_level=87.0),
            IoTDevice(district_id="3273210", device_code="IOT-BDG-CBD-01", fill_level=52.0, volume_m3=0.7, battery_level=92.0),
            IoTDevice(district_id="3273110", device_code="IOT-BDG-CIB-01", fill_level=33.0, volume_m3=0.4, battery_level=98.0),
            IoTDevice(district_id="3273190", device_code="IOT-BDG-CIC-01", fill_level=70.0, volume_m3=1.0, battery_level=85.0),
            IoTDevice(district_id="3273260", device_code="IOT-BDG-CID-01", fill_level=28.0, volume_m3=0.4, battery_level=96.0),
            IoTDevice(district_id="3273121", device_code="IOT-BDG-CNM-01", fill_level=45.0, volume_m3=0.6, battery_level=94.0),
            IoTDevice(district_id="3273230", device_code="IOT-BDG-COB-01", fill_level=67.0, volume_m3=0.9, battery_level=89.0),
            IoTDevice(district_id="3273101", device_code="IOT-BDG-GED-01", fill_level=36.0, volume_m3=0.5, battery_level=97.0),
            IoTDevice(district_id="3273150", device_code="IOT-BDG-KIA-01", fill_level=86.0, volume_m3=1.3, battery_level=75.0),
            IoTDevice(district_id="3273070", device_code="IOT-BDG-LEN-01", fill_level=53.0, volume_m3=0.7, battery_level=91.0),
            IoTDevice(district_id="3273142", device_code="IOT-BDG-MAN-01", fill_level=44.0, volume_m3=0.6, battery_level=96.0),
            IoTDevice(district_id="3273111", device_code="IOT-BDG-PAN-01", fill_level=31.0, volume_m3=0.4, battery_level=98.0),
            IoTDevice(district_id="3273100", device_code="IOT-BDG-RAN-01", fill_level=48.0, volume_m3=0.7, battery_level=90.0),
            IoTDevice(district_id="3273060", device_code="IOT-BDG-REG-01", fill_level=72.0, volume_m3=1.0, battery_level=84.0),
            IoTDevice(district_id="3273240", device_code="IOT-BDG-SKJ-01", fill_level=80.0, volume_m3=1.1, battery_level=82.0),
            IoTDevice(district_id="3273250", device_code="IOT-BDG-SKS-01", fill_level=46.0, volume_m3=0.6, battery_level=95.0),
            IoTDevice(district_id="3273170", device_code="IOT-BDG-SBD-01", fill_level=63.0, volume_m3=0.9, battery_level=88.0),
            IoTDevice(district_id="3273120", device_code="IOT-BDG-UJB-01", fill_level=57.0, volume_m3=0.8, battery_level=91.0),
        ]
        db.session.add_all(iot_seed)

        # 5. Seed Model Registry Metadata
        model_seed = ModelRegistry(
            version="RF-Bandung-v1.0",
            accuracy=96.8,
            r2_score=0.942,
            status="active"
        )
        db.session.add(model_seed)

        # 6. Seed Prediction History Logs
        history_seed = [
            PredictionHistory(district_id="3273030", tanggal=datetime.date.today() - datetime.timedelta(days=1), volume_aktual=18.2, volume_prediksi=19.1, akurasi=95.3, model_version="RF-Bandung-v1.0"),
            PredictionHistory(district_id="3273150", tanggal=datetime.date.today() - datetime.timedelta(days=1), volume_aktual=15.7, volume_prediksi=16.2, akurasi=96.9, model_version="RF-Bandung-v1.0"),
            PredictionHistory(district_id="3273170", tanggal=datetime.date.today() - datetime.timedelta(days=1), volume_aktual=9.4,  volume_prediksi=10.1, akurasi=93.1, model_version="RF-Bandung-v1.0"),
        ]
        db.session.add_all(history_seed)

        db.session.commit()
        logging.info("Database seeding for Bandung successfully completed.")

# If running directly, start the development server
if __name__ == "__main__":
    app = create_app()
    # Bind to all interfaces for flexibility
    app.run(host="127.0.0.1", port=5000, debug=True)
