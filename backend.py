import io
import time
import json
import threading
import base64
import fitz
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pyngrok import ngrok

# ══════════════════════════════════════════════════════════════════════════════
#  SRI LANKA POLICE MOBILE OCR BACKEND
# ══════════════════════════════════════════════════════════════════════════════
# This script provides OCR and PDF processing services for the mobile app
# using Google Cloud Vision API.

# --- CONFIGURATION ---
# The JSON key is gitignored for security
SERVICE_ACCOUNT_FILE = 'google_vision_key.json' 
NGROK_AUTH_TOKEN = "3C0C7gFkX4IQuTy2cMMPHYznbNh_4CZ5YG6ekExX6sBKNfhpv" 
PORT = 5050

app = Flask(__name__)
CORS(app)

# Initialize Google Vision Service
def init_vision():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Error: {SERVICE_ACCOUNT_FILE} not found!")
        return None
    try:
        creds = service_account.Credentials.from_service_account_info(
            json.load(open(SERVICE_ACCOUNT_FILE))
        )
        return build('vision', 'v1', credentials=creds)
    except Exception as e:
        print(f"❌ Error initializing Vision API: {e}")
        return None

vision_service = init_vision()

def get_ocr_text(image_content):
    if not vision_service:
        return "Error: Vision API not initialized"
    
    try:
        content = base64.b64encode(image_content).decode('utf-8')
        request_body = {
            'requests': [{
                'image': {'content': content},
                'features': [{'type': 'DOCUMENT_TEXT_DETECTION'}]
            }]
        }
        response = vision_service.images().annotate(body=request_body).execute()
        
        if response.get('responses') and 'fullTextAnnotation' in response['responses'][0]:
            return response['responses'][0]['fullTextAnnotation']['text']
        return ""
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return f"Error: {str(e)}"

@app.route("/gpu-ocr", methods=["POST", "OPTIONS"])
def gpu_ocr():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})
        
        file = request.files["file"]
        text = get_ocr_text(file.read())
        return jsonify({
            "success": True, 
            "text": text, 
            "final_translation": text # App expects this field
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/translate-pdf", methods=["POST", "OPTIONS"])
def translate_pdf():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})
            
        file = request.files["file"]
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Increase resolution for better OCR
            img_bytes = pix.tobytes("jpg")
            page_text = get_ocr_text(img_bytes)
            full_text += page_text + "\n\n"
            
        return jsonify({
            "success": True, 
            "text": full_text, 
            "final_translation": full_text
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def start_ngrok():
    try:
        ngrok.kill()
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        public_url = ngrok.connect(PORT).public_url
        print("\n" + "="*50)
        print(f"🚀 MOBILE BACKEND IS LIVE!")
        print(f"📡 API URL: {public_url}")
        print(f"🔗 OCR Endpoint: {public_url}/gpu-ocr")
        print(f"🔗 PDF Endpoint: {public_url}/translate-pdf")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ Ngrok Error: {e}")

if __name__ == "__main__":
    if vision_service:
        threading.Thread(target=start_ngrok).start()
        app.run(host="0.0.0.0", port=PORT, debug=False)
    else:
        print("❌ Cannot start server: Vision API failed to initialize.")
