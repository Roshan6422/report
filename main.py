import io
import json
import base64
import fitz
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# We try to get credentials from an environment variable first (for Cloud/Koyeb)
# If not, we look for the local file.
SERVICE_ACCOUNT_FILE = 'google_vision_key.json' 

app = Flask(__name__)
CORS(app)

# Initialize Google Vision Service
def init_vision():
    try:
        # 1. Try to get JSON from Environment Variable (Best for Cloud)
        env_json = os.environ.get('GOOGLE_VISION_CREDENTIALS')
        if env_json:
            print("✅ Using credentials from Environment Variable")
            info = json.loads(env_json)
            creds = service_account.Credentials.from_service_account_info(info)
            return build('vision', 'v1', credentials=creds)
        
        # 2. Try to get from local file
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            print("✅ Using credentials from local file")
            creds = service_account.Credentials.from_service_account_info(
                json.load(open(SERVICE_ACCOUNT_FILE))
            )
            return build('vision', 'v1', credentials=creds)
            
        print("❌ No credentials found!")
        return None
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
        return f"Error: {str(e)}"

@app.route("/gpu-ocr", methods=["POST", "OPTIONS"])
def gpu_ocr():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        file = request.files["file"]
        text = get_ocr_text(file.read())
        return jsonify({"success": True, "text": text, "final_translation": text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/translate-pdf", methods=["POST", "OPTIONS"])
def translate_pdf():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        file = request.files["file"]
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("jpg")
            full_text += get_ocr_text(img_bytes) + "\n\n"
        return jsonify({"success": True, "text": full_text, "final_translation": full_text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Police OCR Backend is Running"}), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=port)
