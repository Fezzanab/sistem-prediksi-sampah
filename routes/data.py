from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models_db.models import District, Horeca, IoTDevice
from models_db.database import db

data_bp = Blueprint("data", __name__)

@data_bp.route("/data")
@login_required
def index():
    """Render data management dashboard with listings of Districts, Horeca, and IoT nodes."""
    districts = District.query.order_by(District.id).all()
    horeca_list = Horeca.query.all()
    iot_devices = IoTDevice.query.all()
    
    # Active tab parameter
    active_tab = request.args.get("tab", "districts")
    
    return render_template(
        "data.html",
        active_page="data",
        active_tab=active_tab,
        districts=districts,
        horeca_list=horeca_list,
        iot_devices=iot_devices
    )

# ─── DISTRICT CRUD ────────────────────────────────────────────────────────────

@data_bp.route("/data/district/add", methods=["POST"])
@login_required
def add_district():
    """Add a new district to the system."""
    d_id = request.form.get("id", "").strip().upper()
    nama = request.form.get("nama", "").strip()
    kecamatan = request.form.get("kecamatan", "").strip()
    
    try:
        populasi = int(request.form.get("populasi", 0))
        luas_wilayah = float(request.form.get("luas_wilayah", 0))
        pendapatan = float(request.form.get("pendapatan", 0))
        wisatawan = int(request.form.get("wisatawan", 0))
    except ValueError:
        flash("Format data numerik tidak valid.", "error")
        return redirect(url_for("data.index", tab="districts"))

    if not d_id or not nama or not kecamatan or populasi <= 0 or luas_wilayah <= 0:
        flash("Mohon lengkapi semua field utama dengan benar.", "error")
        return redirect(url_for("data.index", tab="districts"))

    # Check for duplicate ID
    if District.query.get(d_id):
        flash(f"District dengan ID {d_id} sudah terdaftar.", "error")
        return redirect(url_for("data.index", tab="districts"))

    # Auto-calculate density
    kepadatan = round(populasi / luas_wilayah, 2)

    new_district = District(
        id=d_id,
        nama=nama,
        kecamatan=kecamatan,
        populasi=populasi,
        luas_wilayah=luas_wilayah,
        kepadatan_penduduk=kepadatan,
        pendapatan=pendapatan,
        wisatawan=wisatawan
    )
    
    db.session.add(new_district)
    db.session.commit()
    flash(f"Wilayah {nama} ({d_id}) berhasil ditambahkan.", "success")
    return redirect(url_for("data.index", tab="districts"))

@data_bp.route("/data/district/edit/<id>", methods=["POST"])
@login_required
def edit_district(id):
    """Edit features of an existing district."""
    district = District.query.get_or_404(id)
    nama = request.form.get("nama", "").strip()
    kecamatan = request.form.get("kecamatan", "").strip()
    
    try:
        populasi = int(request.form.get("populasi", 0))
        luas_wilayah = float(request.form.get("luas_wilayah", 0))
        pendapatan = float(request.form.get("pendapatan", 0))
        wisatawan = int(request.form.get("wisatawan", 0))
    except ValueError:
        flash("Format data numerik tidak valid.", "error")
        return redirect(url_for("data.index", tab="districts"))

    if not nama or not kecamatan or populasi <= 0 or luas_wilayah <= 0:
        flash("Mohon lengkapi semua field dengan benar.", "error")
        return redirect(url_for("data.index", tab="districts"))

    # Update district values
    district.nama = nama
    district.kecamatan = kecamatan
    district.populasi = populasi
    district.luas_wilayah = luas_wilayah
    district.kepadatan_penduduk = round(populasi / luas_wilayah, 2)
    district.pendapatan = pendapatan
    district.wisatawan = wisatawan
    
    db.session.commit()
    flash(f"Data wilayah {nama} berhasil diperbarui.", "success")
    return redirect(url_for("data.index", tab="districts"))

@data_bp.route("/data/district/delete/<id>", methods=["POST"])
@login_required
def delete_district(id):
    """Delete a district from the system."""
    district = District.query.get_or_404(id)
    name = district.nama
    db.session.delete(district)
    db.session.commit()
    flash(f"Wilayah {name} berhasil dihapus dari sistem.", "success")
    return redirect(url_for("data.index", tab="districts"))

# ─── HORECA CRUD ──────────────────────────────────────────────────────────────

@data_bp.route("/data/horeca/add", methods=["POST"])
@login_required
def add_horeca():
    """Add a new Horeca business listing."""
    district_id = request.form.get("district_id", "").strip()
    nama_usaha = request.form.get("nama_usaha", "").strip()
    jenis = request.form.get("jenis", "").strip()
    
    try:
        waste_index = float(request.form.get("waste_index", 0.0))
    except ValueError:
        flash("Waste index harus berupa angka numerik.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    if not district_id or not nama_usaha or not jenis or waste_index <= 0:
        flash("Lengkapi semua field untuk data Horeca.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    # Verify district exists
    if not District.query.get(district_id):
        flash("ID District tidak terdaftar di sistem.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    new_horeca = Horeca(
        district_id=district_id,
        nama_usaha=nama_usaha,
        jenis=jenis,
        waste_index=waste_index
    )
    
    db.session.add(new_horeca)
    db.session.commit()
    flash(f"Horeca {nama_usaha} berhasil ditambahkan.", "success")
    return redirect(url_for("data.index", tab="horeca"))

@data_bp.route("/data/horeca/edit/<int:id>", methods=["POST"])
@login_required
def edit_horeca(id):
    """Edit an existing Horeca business entry."""
    horeca = Horeca.query.get_or_404(id)
    district_id = request.form.get("district_id", "").strip()
    nama_usaha = request.form.get("nama_usaha", "").strip()
    jenis = request.form.get("jenis", "").strip()
    
    try:
        waste_index = float(request.form.get("waste_index", 0.0))
    except ValueError:
        flash("Waste index harus berupa angka numerik.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    if not district_id or not nama_usaha or not jenis or waste_index <= 0:
        flash("Lengkapi semua field Horeca.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    if not District.query.get(district_id):
        flash("ID District tidak terdaftar.", "error")
        return redirect(url_for("data.index", tab="horeca"))

    horeca.district_id = district_id
    horeca.nama_usaha = nama_usaha
    horeca.jenis = jenis
    horeca.waste_index = waste_index
    
    db.session.commit()
    flash(f"Data Horeca {nama_usaha} berhasil diperbarui.", "success")
    return redirect(url_for("data.index", tab="horeca"))

@data_bp.route("/data/horeca/delete/<int:id>", methods=["POST"])
@login_required
def delete_horeca(id):
    """Delete a Horeca record."""
    horeca = Horeca.query.get_or_404(id)
    name = horeca.nama_usaha
    db.session.delete(horeca)
    db.session.commit()
    flash(f"Horeca {name} berhasil dihapus.", "success")
    return redirect(url_for("data.index", tab="horeca"))

# ─── IOT DEVICES CRUD ─────────────────────────────────────────────────────────

@data_bp.route("/data/iot/add", methods=["POST"])
@login_required
def add_iot():
    """Add a new IoT sensor node to the system."""
    district_id = request.form.get("district_id", "").strip()
    device_code = request.form.get("device_code", "").strip().upper()
    
    try:
        fill_level = float(request.form.get("fill_level", 0.0))
        volume_m3 = float(request.form.get("volume_m3", 0.0))
        battery_level = float(request.form.get("battery_level", 100.0))
    except ValueError:
        flash("Format data numerik untuk IoT sensor salah.", "error")
        return redirect(url_for("data.index", tab="iot"))

    if not district_id or not device_code:
        flash("Lengkapi field utama untuk sensor IoT.", "error")
        return redirect(url_for("data.index", tab="iot"))

    # Verify duplicate code
    if IoTDevice.query.filter_by(device_code=device_code).first():
        flash(f"Kode perangkat IoT {device_code} sudah digunakan.", "error")
        return redirect(url_for("data.index", tab="iot"))

    if not District.query.get(district_id):
        flash("ID District tidak terdaftar.", "error")
        return redirect(url_for("data.index", tab="iot"))

    new_device = IoTDevice(
        district_id=district_id,
        device_code=device_code,
        fill_level=fill_level,
        volume_m3=volume_m3,
        battery_level=battery_level
    )
    
    db.session.add(new_device)
    db.session.commit()
    flash(f"Perangkat IoT {device_code} terdaftar.", "success")
    return redirect(url_for("data.index", tab="iot"))

@data_bp.route("/data/iot/edit/<int:id>", methods=["POST"])
@login_required
def edit_iot(id):
    """Edit properties of a registered IoT sensor node."""
    device = IoTDevice.query.get_or_404(id)
    district_id = request.form.get("district_id", "").strip()
    device_code = request.form.get("device_code", "").strip().upper()
    
    try:
        fill_level = float(request.form.get("fill_level", 0.0))
        volume_m3 = float(request.form.get("volume_m3", 0.0))
        battery_level = float(request.form.get("battery_level", 100.0))
    except ValueError:
        flash("Format data numerik untuk IoT sensor salah.", "error")
        return redirect(url_for("data.index", tab="iot"))

    if not district_id or not device_code:
        flash("Lengkapi field data sensor IoT.", "error")
        return redirect(url_for("data.index", tab="iot"))

    # Verify duplicate code on other nodes
    dup = IoTDevice.query.filter_by(device_code=device_code).first()
    if dup and dup.id != id:
        flash(f"Kode perangkat {device_code} sudah digunakan perangkat lain.", "error")
        return redirect(url_for("data.index", tab="iot"))

    if not District.query.get(district_id):
        flash("ID District tidak terdaftar.", "error")
        return redirect(url_for("data.index", tab="iot"))

    device.district_id = district_id
    device.device_code = device_code
    device.fill_level = fill_level
    device.volume_m3 = volume_m3
    device.battery_level = battery_level
    
    db.session.commit()
    flash(f"Sensor IoT {device_code} berhasil diperbarui.", "success")
    return redirect(url_for("data.index", tab="iot"))

@data_bp.route("/data/iot/delete/<int:id>", methods=["POST"])
@login_required
def delete_iot(id):
    """Deregister an IoT device."""
    device = IoTDevice.query.get_or_404(id)
    code = device.device_code
    db.session.delete(device)
    db.session.commit()
    flash(f"Sensor IoT {code} berhasil dihapus.", "success")
    return redirect(url_for("data.index", tab="iot"))
