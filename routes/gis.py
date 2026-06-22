from flask import Blueprint, render_template, jsonify, current_app
from routes.auth import login_required
from models_db.models import District, PredictionHistory
import os
import json
import random

gis_bp = Blueprint("gis", __name__)

def _compute_district_metrics(d):
    """Compute prediction metrics for a given district ORM object."""
    base_vol = (d.populasi * 0.00015) + (d.luas_wilayah * 0.1)
    horeca_mul = 1.0 + (d.total_horeca_waste_index * 0.05)
    iot_mul    = 1.0 + (d.avg_iot_fill_level * 0.002)
    aktual     = round(base_vol * horeca_mul * iot_mul, 1)
    # deterministic jitter based on id hash so values are stable across requests
    jitter     = (abs(hash(d.id)) % 7) / 100  # 0.00 – 0.06
    prediksi   = round(aktual * (1.02 + jitter), 1)

    if prediksi > 15.0:
        status = "overflow"
    elif prediksi > 9.0:
        status = "kritis"
    else:
        status = "normal"

    return aktual, prediksi, status


@gis_bp.route("/gis")
@login_required
def index():
    """Render a fullscreen Leaflet GIS page for Kota Bandung.

    The page will load GeoJSON from `/api/gis/data` and render a choropleth
    based on `volume_prediksi` returned in the feature properties.
    """
    # Provide a small set of summary stats to display if needed by template
    districts = District.query.count()
    return render_template("gis_fullscreen.html", active_page="gis", total_districts=districts)


@gis_bp.route("/api/gis/data")
@login_required
def get_geojson_data():
    """
    Load the Bandung kecamatan GeoJSON, enrich it with live DB metrics,
    and return the decorated FeatureCollection for choropleth mapping.
    """
    geojson_path = os.path.join(
        current_app.root_path,
        "static", "geojson", "bandung_kecamatan_selected_30.geojson"
    )

    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "GeoJSON file not found", "path": geojson_path}), 404

    # Build lookup by id_kecamatan (matches District.id in our seed)
    all_districts = {d.id: d for d in District.query.all()}

    for feature in geojson.get("features", []):
        props  = feature.setdefault("properties", {})
        kec_id = props.get("id_kecamatan")
        district = all_districts.get(kec_id)

        if district:
            aktual, prediksi, status = _compute_district_metrics(district)

            props["district_db_id"]   = district.id
            props["nama"]             = district.kecamatan
            props["populasi"]         = district.populasi
            props["luas_wilayah"]     = district.luas_wilayah
            props["kepadatan"]        = district.kepadatan_penduduk
            props["pendapatan"]       = district.pendapatan
            props["wisatawan"]        = district.wisatawan
            props["horeca_index"]     = round(district.total_horeca_waste_index, 2)
            props["iot_fill_level"]   = round(district.avg_iot_fill_level, 1)
            props["volume_harian"]    = aktual
            props["volume_prediksi"]  = prediksi
            props["status"]           = status
            props["difference"]       = round(prediksi - aktual, 1)
        else:
            # District not in DB yet — mark as unknown
            props["nama"]            = props.get("nama_kecamatan", "Unknown")
            props["status"]          = "normal"
            props["volume_prediksi"] = 0
            props["volume_harian"]   = 0
            props["difference"]      = 0
            props["populasi"]        = 0
            props["luas_wilayah"]    = 0
            props["horeca_index"]    = 0
            props["iot_fill_level"]  = 0

    return jsonify(geojson)
