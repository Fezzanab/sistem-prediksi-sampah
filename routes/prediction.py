from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models_db.models import District, PredictionHistory, ModelRegistry
from models_db.database import db
from services.ai_client import AIClient
import datetime

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/prediction")
@login_required
def index():
    """Render the AI predictive control screen and history."""
    districts = District.query.order_by(District.id).all()
    models = ModelRegistry.query.order_by(ModelRegistry.trained_at.desc()).all()
    history = PredictionHistory.query.order_by(PredictionHistory.id.desc()).limit(10).all()
    
    # Check if there is a recent prediction result in the session
    prediction_result = session.pop("prediction_result", None)
    
    # Active model details
    active_model = ModelRegistry.query.filter_by(status="active").order_by(ModelRegistry.trained_at.desc()).first()
    
    return render_template(
        "prediction.html",
        active_page="prediction",
        districts=districts,
        models=models,
        history=history,
        prediction_result=prediction_result,
        active_model=active_model
    )

@prediction_bp.route("/prediction/run", methods=["POST"])
@login_required
def run_prediction():
    """Submit features to the FastAPI service and capture predictions."""
    district_id = request.form.get("district_id", "")
    
    # Retrieve form variables (editable by user for what-if scenarios)
    try:
        features = {
            "populasi": int(request.form.get("populasi", 0)),
            "luas_wilayah": float(request.form.get("luas_wilayah", 0)),
            "kepadatan_penduduk": float(request.form.get("kepadatan_penduduk", 0)),
            "pendapatan": float(request.form.get("pendapatan", 0)),
            "wisatawan": int(request.form.get("wisatawan", 0)),
            "horeca": float(request.form.get("horeca", 0)),
            "iot": float(request.form.get("iot", 0))
        }
    except ValueError:
        flash("Parameter input prediksi harus bernilai numerik.", "error")
        return redirect(url_for("prediction.index"))

    district = District.query.get(district_id)
    if not district:
        flash("Pilih wilayah kecamatan yang valid.", "error")
        return redirect(url_for("prediction.index"))

    # Call FastAPI service via REST client
    result = AIClient.predict(features)
    
    # Calculate baseline actual volume (estimate based on database features)
    base_vol = (district.populasi * 0.00015) + (district.luas_wilayah * 0.1)
    horeca_mul = 1.0 + (district.total_horeca_waste_index * 0.05)
    iot_mul = 1.0 + (district.avg_iot_fill_level * 0.002)
    actual_volume = round(base_vol * horeca_mul * iot_mul, 2)
    
    # Save to history table
    new_run = PredictionHistory(
        district_id=district.id,
        tanggal=datetime.date.today(),
        volume_aktual=actual_volume,
        volume_prediksi=result["prediction"],
        akurasi=result["confidence"],
        model_version=result["model_version"]
    )
    
    db.session.add(new_run)
    db.session.commit()
    
    # Store result details in session to render in dashboard card
    session["prediction_result"] = {
        "district_id": district.id,
        "district_name": district.nama,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "armada_needed": result["armada_needed"],
        "rekomendasi": result["rekomendasi"],
        "is_mock": result["is_mock"],
        "model_version": result["model_version"],
        "actual_volume": actual_volume,
        "difference": round(result["prediction"] - actual_volume, 2)
    }
    
    flash("Prediksi model AI berhasil diselesaikan.", "success")
    return redirect(url_for("prediction.index"))

@prediction_bp.route("/prediction/train", methods=["POST"])
@login_required
def train_model():
    """Trigger AI training on FastAPI and register the output in the DB."""
    # Call FastAPI model train endpoint
    result = AIClient.train_model()
    
    if result.get("success"):
        # Archive previous models
        ModelRegistry.query.update({ModelRegistry.status: "archive"})
        
        # Add new trained model
        new_model = ModelRegistry(
            version=result["version"],
            accuracy=result["accuracy"],
            r2_score=result["r2_score"],
            status="active"
        )
        db.session.add(new_model)
        db.session.commit()
        
        mode = "MOCK" if result.get("is_mock") else "PRODUCTION"
        flash(f"Model [{mode}] {result['version']} sukses dilatih. R2: {result['r2_score']}, Akurasi: {result['accuracy']}%", "success")
    else:
        flash("Gagal memproses training model AI di microservice.", "error")
        
    return redirect(url_for("prediction.index"))
