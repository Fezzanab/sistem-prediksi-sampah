import requests
import logging
import random
from flask import current_app

class AIClient:
    @staticmethod
    def get_api_url():
        """Retrieve the FastAPI base URL from application configuration."""
        try:
            return current_app.config.get("FASTAPI_API_URL", "http://localhost:8000")
        except RuntimeError:
            # Fallback when outside application context
            return "http://localhost:8000"

    @classmethod
    def check_health(cls):
        """Checks if the FastAPI service is online."""
        url = cls.get_api_url()
        try:
            # Try to connect with a short timeout
            response = requests.get(f"{url}/", timeout=1.5)
            return response.status_code == 200
        except Exception:
            return False

    @classmethod
    def predict(cls, features):
        """
        Sends feature data to FastAPI `/predict` endpoint.
        Falls back to local RF regression formula if FastAPI is offline.
        """
        url = f"{cls.get_api_url()}/predict"
        
        # Prepare inputs
        payload = {
            "populasi": int(features.get("populasi", 0)),
            "horeca": float(features.get("horeca", 0.0)),
            "iot": float(features.get("iot", 0.0)),
            "wisatawan": int(features.get("wisatawan", 0)),
            "kepadatan_penduduk": float(features.get("kepadatan_penduduk", 0.0)),
            "pendapatan": float(features.get("pendapatan", 0.0)),
            "luas_wilayah": float(features.get("luas_wilayah", 0.0))
        }

        try:
            logging.info(f"Calling FastAPI prediction endpoint: {url}")
            response = requests.post(url, json=payload, timeout=3.0)
            if response.status_code == 200:
                result = response.json()
                result["is_mock"] = False
                return result
            else:
                logging.warning(f"FastAPI prediction returned status code {response.status_code}. Using fallback prediction.")
        except Exception as e:
            logging.warning(f"Failed to connect to FastAPI microservice for prediction ({e}). Using local mock fallback.")

        # FALLBACK MOCK PREDICTION LOGIC (Simulates a Random Forest Regressor model)
        # Base factor based on population, area, tourists, horeca, and IoT
        base = (payload["populasi"] * 0.00015) + (payload["luas_wilayah"] * 0.1)
        horeca_multiplier = 1.0 + (payload["horeca"] * 0.05)
        iot_multiplier = 1.0 + (payload["iot"] * 0.002) # sensors fill level impact
        tourist_multiplier = 1.0 + (payload["wisatawan"] * 0.00002)
        income_multiplier = 1.0 + (payload["pendapatan"] / 20000000.0) # higher income generate slightly more waste
        
        predicted_vol = base * horeca_multiplier * iot_multiplier * tourist_multiplier * income_multiplier
        # Ensure positive prediction
        predicted_vol = max(0.1, round(predicted_vol, 2))
        
        accuracy = round(94.5 + random.random() * 4.0, 2) # mock accuracy
        armada = max(1, int(predicted_vol / 3.5) + (1 if (predicted_vol % 3.5) > 0.5 else 0))
        
        # Recommendations
        if predicted_vol > 15.0:
            rekomendasi = "Tingkat timbulan sangat tinggi. Kerahkan armada tambahan tipe Heavy Compactor. Jadwalkan penjemputan 2x sehari."
        elif predicted_vol > 8.0:
            rekomendasi = "Tingkat timbulan sedang-tinggi. Jadwalkan penjemputan rutin harian dan monitoring sensor IoT."
        else:
            rekomendasi = "Tingkat timbulan normal. Cukup penjemputan berkala sesuai jadwal standar."

        return {
            "prediction": predicted_vol,
            "confidence": accuracy,
            "armada_needed": armada,
            "rekomendasi": rekomendasi,
            "is_mock": True,
            "model_version": "RF-Default-v1.0"
        }

    @classmethod
    def train_model(cls):
        """
        Triggers model training on FastAPI `/train` endpoint.
        Falls back to local mock training response if FastAPI is offline.
        """
        url = f"{cls.get_api_url()}/train"
        try:
            logging.info(f"Calling FastAPI train endpoint: {url}")
            response = requests.post(url, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                result["is_mock"] = False
                return result
            else:
                logging.warning(f"FastAPI train returned status code {response.status_code}. Using fallback training.")
        except Exception as e:
            logging.warning(f"Failed to connect to FastAPI microservice for training ({e}). Using local mock training.")

        # Fallback Mock training result
        import datetime
        version = f"RF-{datetime.datetime.now().strftime('%Y%m%d')}-v{random.randint(1,9)}"
        accuracy = round(96.2 + random.random() * 2.0, 2)
        r2_score = round(0.92 + random.random() * 0.06, 3)
        
        return {
            "success": True,
            "version": version,
            "accuracy": accuracy,
            "r2_score": r2_score,
            "is_mock": True,
            "message": "Model training simulated successfully. New model registered in memory."
        }
