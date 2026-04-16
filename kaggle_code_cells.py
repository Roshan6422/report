# ══════════════════════════════════════════════════════════════════════════
# CELL 1: Install Dependencies
# ══════════════════════════════════════════════════════════════════════════
 
# FIX: numpy version pinned < 2.0 to prevent surya binary incompatibility
# FIX: transformers version pinned for better stability with older architectures
# NOTE: Jupyter magic commands commented out for Python compatibility
# Run these manually in your terminal or Jupyter notebook
# !pip install --quiet \
#     "numpy<2.0.0" \
#     surya-ocr \
#     Pillow \
#     flask \
#     "pyngrok==7.2.2" \
#     "transformers>=4.37.0,<5.0.0" \
#     "requests>=2.31.0"
 
# NOTE: Jupyter magic commands commented out for Python compatibility
# Run these manually in your terminal or Jupyter notebook
# !sudo apt-get install -y zstd > /dev/null 2>&1
 
# Install Ollama
# NOTE: Jupyter magic commands commented out for Python compatibility
# Run these manually in your terminal or Jupyter notebook
# !curl -fsSL https://ollama.com/install.sh | sh
 
import numpy as np
import torch
 
print(f"✅ NumPy:   {np.__version__}")
print(f"✅ PyTorch: {torch.__version__}")
print(f"✅ CUDA:    {torch.cuda.is_available()}")
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        mem  = torch.cuda.get_device_properties(i).total_memory // (1024**3)
        print(f"✅ GPU[{i}]:  {name}  ({mem} GB)")
 # ══════════════════════════════════════════════════════════════════════════
# CELL 2: Start Ollama + Create Police AI Model
# ══════════════════════════════════════════════════════════════════════════
 
import os, time, subprocess, json
 
# --- Start Ollama server ---
ollama_proc = subprocess.Popen(
    ["ollama", "serve"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(6)
print(f"✅ Ollama started  (PID: {ollama_proc.pid})")
 
# --- Check if model already downloaded (save time on reruns) ---
try:
    import requests as _req
    tags = _req.get("http://localhost:11434/api/tags", timeout=5).json()
    existing = [m["name"] for m in tags.get("models", [])]
except Exception:
    existing = []
 
if "gemma2:9b" not in existing:
    print("📥 Downloading Gemma2 9B (first time only, ~5 GB)...")
    # Note: In a real Python script, you would use subprocess instead of !
    # subprocess.run(["ollama", "pull", "gemma2:9b"], check=True)
    print("Run: ollama pull gemma2:9b")
else:
    print("✅ Gemma2 9B already downloaded — skip pull")
 
# --- Build Modelfile ---
# FIX: Use a proper heredoc-style write so the SYSTEM block is clean
SYSTEM_PROMPT = """You are the Sovereign Sri Lanka Police AI Architect.
Your primary directive is Institutional Integrity and Factual Zero-Hallucination.
You ONLY output valid JSON. Never add explanation, markdown, or extra text.
 
OFFENCE CLASSIFICATION:
- Category 01: Terrorist Activities
- Category 02: Recovery of Arms & Ammunition
- Category 03: Protests & Strikes
- Category 04: SERIOUS CRIMES COMMITTED (Includes Homicides)
- Category 05: Robberies
- Category 06: Thefts of Vehicles
- Category 07: Thefts of Properties
- Category 08: House Breaking & Theft
- Category 09: Rape, Sexual Abuse & Child Abuse
- Category 10: FATAL ACCIDENTS
- Category 11: Unidentified dead bodies & suspicious dead bodies
- Category 12: Police Accidents
- Category 13: Serious injuries of Police officers and Damages to Police property
- Category 14: Misconducts of Police officers
- Category 15: Deaths of Police officers
- Category 16: Hospital admission of SGOFO
- Category 17: Passing away of close relatives of SGOFO
- Category 18: Passing away of close relatives of retired SGOFO
- Category 19: Detentions of Narcotics & Illicit Liquor
- Category 20: Arrests
- Category 21: Arresting of Tri-Forces Members
- Category 22: Disappearances
- Category 23: Suicides
- Category 24: Incidents regarding Foreigners
- Category 25: Wild elephant attacks & deaths of wild elephants
- Category 26: Deaths due to drowning
- Category 27: Incidents of Fire
- Category 28: Other Matters



EXTRACTION PROTOCOL:
- DATE: YYYY-MM-DD format. Default: "N/A"
- TIME: 24-hour HHMM format (e.g. 1430). Default: "N/A"
- DESCRIPTION: Formal, clinical Police English. No assumptions. 
- REPETITION CONTROL: Never repeat phrases or sentences. Ensure a single, cohesive narrative.
- FINANCIAL_LOSS: Numeric string in LKR. Use "N/A" if none.
- STATUS: One of → Arrested | Fled | Under Investigation | Recovered | Unknown
- CATEGORY: Use numeric code only (e.g. "04")
 
JSON OUTPUT SCHEMA (return ONLY this, nothing else):
{
  "station": "",
  "division": "",
  "date": "",
  "time": "",
  "category": "",
  "description": "",
  "financial_loss": "",
  "status": "",
  "victim_names": [],
  "suspect_names": [],
  "vehicle_numbers": [],
  "locations": []
}"""
 
# FIX: Write Modelfile correctly — triple quotes inside f-string causes bugs
# Use explicit marker instead
modelfile_content = 'FROM gemma2:9b\n'
modelfile_content += 'PARAMETER temperature 0.05\n'
modelfile_content += 'PARAMETER num_ctx 32768\n'
modelfile_content += 'PARAMETER top_p 0.9\n'
modelfile_content += 'PARAMETER repeat_penalty 1.5\n'
modelfile_content += 'PARAMETER stop "<|im_start|>"\n'
modelfile_content += 'PARAMETER stop "<|im_end|>"\n'
modelfile_content += 'PARAMETER stop "<|file_separator|>"\n'
modelfile_content += 'SYSTEM """\n'
modelfile_content += SYSTEM_PROMPT.strip()
modelfile_content += '\n"""\n'
 
with open("Modelfile", "w", encoding="utf-8") as f:
    f.write(modelfile_content)
 
# Verify the file looks right
print("\n--- Modelfile preview (first 10 lines) ---")
with open("Modelfile") as f:
    for i, line in enumerate(f):
        if i < 10: print(f"  {line}", end="")
print("\n---")
 
print("\n🔨 Building police-ai-master:latest...")
# NOTE: Jupyter magic commands commented out for Python compatibility
# Run these manually in your terminal or Jupyter notebook
# !ollama create police-ai-master:latest -f Modelfile
 
# Verify
result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
print(result.stdout)
 
if "police-ai-master" in result.stdout:
    print("✅ Police AI Model ready!")
else:
    print("❌ Model creation failed — check Modelfile above")
 # ══════════════════════════════════════════════════════════════════════════
# CELL 4: Load Surya OCR
# ══════════════════════════════════════════════════════════════════════════
 
import torch, time as _time
 
print("🧠 Loading Surya OCR into GPU...")
t0 = _time.time()
 
# FIX: Surya changed its API multiple times. Try new API first, then old.
SURYA_LOADED   = False
recognition_predictor = None
detection_predictor   = None
foundation_predictor  = None
surya_api_version     = None
 
# --- Try NEW API (surya >= 0.8) ---
try:
    from surya.recognition import RecognitionPredictor
    from surya.detection  import DetectionPredictor
 
    # Some versions also need FoundationPredictor
    try:
        from surya.foundation import FoundationPredictor
        foundation_predictor  = FoundationPredictor()
        recognition_predictor = RecognitionPredictor(foundation_predictor)
        surya_api_version = "new-foundation"
    except ImportError:
        recognition_predictor = RecognitionPredictor()
        surya_api_version = "new-simple"
 
    detection_predictor = DetectionPredictor()
    SURYA_LOADED = True
    print(f"✅ Surya API: {surya_api_version}")
 
except Exception as e1:
    print(f"⚠️ New Surya API failed ({e1}) — trying legacy API...")
 
    # --- Try OLD API (surya < 0.6) ---
    try:
        from surya.model.detection.model    import load_model as load_det_model, load_processor as load_det_processor
        from surya.model.recognition.model  import load_model as load_rec_model
        from surya.model.recognition.processor import load_processor as load_rec_processor
        from surya.ocr import run_ocr
 
        det_processor = load_det_processor()
        det_model     = load_det_model()
        rec_model     = load_rec_model()
        rec_processor = load_rec_processor()
 
        # Wrap into a callable so Flask code stays the same
        class _LegacyOCR:
            def __call__(self, images, langs=None, **kwargs):
                return run_ocr(images, [langs or ["en", "si"]] * len(images),
                               det_model, det_processor, rec_model, rec_processor)
 
        recognition_predictor = _LegacyOCR()
        detection_predictor   = None   # included inside run_ocr for legacy
        SURYA_LOADED          = True
        surya_api_version     = "legacy"
        print("✅ Surya API: legacy")
 
    except Exception as e2:
        print(f"❌ Both Surya APIs failed.\n  New: {e1}\n  Old: {e2}")
        SURYA_LOADED = False
 
if SURYA_LOADED:
    elapsed = _time.time() - t0
    print(f"✅ Surya OCR loaded in {elapsed:.1f}s")
else:
    print("⚠️  Running without OCR — AI endpoint still works")
 # ══════════════════════════════════════════════════════════════════════════
# CELL 5: Flask API Server
# ══════════════════════════════════════════════════════════════════════════
 
import threading, io, traceback, logging
from flask import Flask, request, jsonify, Response
from PIL  import Image
import requests as _req
 
# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt = "%H:%M:%S"
)
log = logging.getLogger("police-ai")
 
app      = Flask(__name__)
gpu_lock = threading.Lock()   # Surya KV cache is NOT thread-safe
 
MAX_IMAGE_BYTES = 20 * 1024 * 1024   # 20 MB limit
OLLAMA_BASE     = "http://localhost:11434"
 
# ── Stats counter ─────────────────────────────────────────────────────────
from collections import defaultdict
import datetime
 
_stats = defaultdict(int)
_start_time = datetime.datetime.utcnow()
 
def _bump(key):
    _stats[key] += 1
 
# ── Helpers ───────────────────────────────────────────────────────────────
def _extract_surya_text(predictions):
    """
    FIX: Surya returns different object shapes across versions.
    This handles all known shapes.
    """
    lines = []
    if not predictions:
        return ""
 
    page = predictions[0]
 
    # New API: object with .text_lines attribute
    if hasattr(page, "text_lines"):
        for line in page.text_lines:
            txt = getattr(line, "text", None) or (line.get("text", "") if isinstance(line, dict) else "")
            if txt and txt.strip():
                lines.append(txt.strip())
 
    # Old API: dict
    elif isinstance(page, dict):
        for line in page.get("text_lines", []):
            if isinstance(line, dict):
                txt = line.get("text", "")
            else:
                txt = getattr(line, "text", "")
            if txt and txt.strip():
                lines.append(txt.strip())
 
    # Some versions return list of strings directly
    elif isinstance(page, list):
        for item in page:
            txt = item if isinstance(item, str) else getattr(item, "text", "")
            if txt and txt.strip():
                lines.append(txt.strip())
 
    return "\n".join(lines)
 
 
def _ollama_post(endpoint, data, stream=False, timeout=300):
    """Proxy to Ollama with retry logic."""
    url = f"{OLLAMA_BASE}/{endpoint.lstrip('/')}"
    for attempt in range(3):
        try:
            resp = _req.post(url, json=data, timeout=timeout, stream=stream)
            return resp
        except _req.exceptions.ConnectionError:
            if attempt < 2:
                log.warning(f"Ollama connection failed (attempt {attempt+1}), retrying…")
                time.sleep(2)
            else:
                raise
 
 
# ══════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════
 
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service"    : "Sri Lanka Police AI Cloud v2.0",
        "status"     : "online",
        "surya_ocr"  : SURYA_LOADED,
        "surya_api"  : surya_api_version,
        "ollama"     : True,
        "models"     : [m["name"] for m in _req.get(f"{OLLAMA_BASE}/api/tags").json().get("models", [])] if True else [],
        "endpoints"  : ["/health", "/stats", "/gpu-ocr", "/process", "/api/generate", "/api/chat", "/api/tags"]
    })
 
@app.route("/health", methods=["GET"])
def health():
    # Check Ollama alive
    try:
        _req.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        ollama_ok = True
    except Exception:
        ollama_ok = False
 
    return jsonify({
        "status"   : "ok" if ollama_ok else "degraded",
        "surya"    : SURYA_LOADED,
        "ollama"   : ollama_ok,
        "gpu_mem_free_gb" : round(
            torch.cuda.memory_reserved(0) / 1e9, 2
        ) if torch.cuda.is_available() else None
    })
 
@app.route("/stats", methods=["GET"])
def stats():
    uptime = (datetime.datetime.utcnow() - _start_time).total_seconds()
    return jsonify({
        "uptime_minutes" : round(uptime / 60, 1),
        "requests"       : dict(_stats)
    })
 
 
# ── OCR Endpoint ──────────────────────────────────────────────────────────
@app.route("/gpu-ocr", methods=["POST"])
def gpu_ocr():
    _bump("ocr")
    try:
        if not SURYA_LOADED:
            return jsonify({"success": False, "error": "Surya OCR not loaded"}), 503
 
        if "file" not in request.files:
            return jsonify({"success": False, "error": "Send image as 'file' in multipart form"}), 400
 
        raw = request.files["file"].read()
        if len(raw) < 100:
            return jsonify({"success": False, "error": "File too small or empty"}), 400
        if len(raw) > MAX_IMAGE_BYTES:
            return jsonify({"success": False, "error": f"File too large (max {MAX_IMAGE_BYTES//1024//1024} MB)"}), 413
 
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        log.info(f"[OCR] {image.size[0]}x{image.size[1]} px")
 
        t0 = _time.time()
        with gpu_lock:
            if surya_api_version == "legacy":
                predictions = recognition_predictor([image])
            elif detection_predictor is not None:
                predictions = recognition_predictor([image], det_predictor=detection_predictor)
            else:
                predictions = recognition_predictor([image])
            # FIX: Always free GPU cache after inference
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
 
        text    = _extract_surya_text(predictions)
        elapsed = round(_time.time() - t0, 2)
        lines   = len([l for l in text.split("\n") if l.strip()])
        log.info(f"[OCR] ✅ {lines} lines | {len(text)} chars | {elapsed}s")
 
        return jsonify({"success": True, "text": text, "lines": lines, "time_sec": elapsed})
 
    except Exception as e:
        traceback.print_exc()
        _bump("ocr_error")
        return jsonify({"success": False, "error": str(e)}), 500
 
 
# ── NEW: Combined OCR + AI Extract in one call ────────────────────────────
@app.route("/process", methods=["POST"])
def process():
    """
    NEW ENDPOINT — most useful for the app.
    POST multipart/form-data:
      file   = image file (required)
      model  = ollama model name (optional, default: police-ai-master)
      prompt = custom prompt override (optional)
 
    Returns: { ocr_text, ai_json, ocr_time, ai_time }
    """
    _bump("process")
    try:
        # 1. OCR
        if not SURYA_LOADED:
            return jsonify({"success": False, "error": "Surya OCR not loaded"}), 503
        if "file" not in request.files:
            return jsonify({"success": False, "error": "Send image as 'file' in multipart form"}), 400
 
        raw = request.files["file"].read()
        if len(raw) < 100:
            return jsonify({"success": False, "error": "File too small"}), 400
        if len(raw) > MAX_IMAGE_BYTES:
            return jsonify({"success": False, "error": "File too large"}), 413
 
        image = Image.open(io.BytesIO(raw)).convert("RGB")
 
        t0 = _time.time()
        with gpu_lock:
            if surya_api_version == "legacy":
                predictions = recognition_predictor([image])
            elif detection_predictor is not None:
                predictions = recognition_predictor([image], det_predictor=detection_predictor)
            else:
                predictions = recognition_predictor([image])
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
 
        ocr_text = _extract_surya_text(predictions)
        ocr_time = round(_time.time() - t0, 2)
        log.info(f"[PROCESS] OCR done: {len(ocr_text)} chars in {ocr_time}s")
 
        # 2. AI Extraction
        model  = request.form.get("model", "police-ai-master:latest")
        prompt = request.form.get("prompt") or (
            f"Extract all police report fields from the following OCR text and return ONLY valid JSON:\n\n{ocr_text}"
        )
 
        t1 = _time.time()
        resp = _ollama_post("/api/generate", {
            "model" : model,
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        ai_time = round(_time.time() - t1, 2)
 
        raw_ai = resp.json().get("response", "")
 
        # Try to parse AI output as JSON
        ai_json = None
        try:
            # Strip markdown fences if present
            clean = raw_ai.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            ai_json = json.loads(clean)
        except Exception:
            ai_json = {"raw_response": raw_ai}
 
        log.info(f"[PROCESS] AI done in {ai_time}s")
        return jsonify({
            "success" : True,
            "ocr_text": ocr_text,
            "ai_json" : ai_json,
            "ocr_time": ocr_time,
            "ai_time" : ai_time
        })
 
    except Exception as e:
        traceback.print_exc()
        _bump("process_error")
        return jsonify({"success": False, "error": str(e)}), 500
 
 
# ── Ollama Proxy Endpoints ─────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def ollama_generate():
    _bump("generate")
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400
 
        is_stream = data.get("stream", False)
        resp = _ollama_post("/api/generate", data, stream=is_stream, timeout=300)
 
        if is_stream:
            def gen():
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            return Response(gen(), content_type=resp.headers.get("Content-Type", "application/json"))
        else:
            return jsonify(resp.json()), resp.status_code
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
@app.route("/api/chat", methods=["POST"])
def ollama_chat():
    _bump("chat")
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        is_stream = data.get("stream", False)
        resp = _ollama_post("/api/chat", data, stream=is_stream, timeout=300)
        if is_stream:
            def gen():
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk: yield chunk
            return Response(gen(), content_type=resp.headers.get("Content-Type", "application/json"))
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
@app.route("/api/tags", methods=["GET"])
def ollama_tags():
    try:
        resp = _req.get(f"{OLLAMA_BASE}/api/tags", timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
@app.route("/api/embeddings", methods=["POST"])
def ollama_embeddings():
    """Bonus: embeddings endpoint for vector search features."""
    _bump("embeddings")
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        resp = _ollama_post("/api/embeddings", data, timeout=60)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
print("✅ Flask routes registered:")
print("   GET  /           → Info")
print("   GET  /health     → Health check")
print("   GET  /stats      → Request stats")
print("   POST /gpu-ocr    → Surya OCR only")
print("   POST /process    → OCR + AI extract (NEW)")
print("   POST /api/generate  → Ollama generate")
print("   POST /api/chat      → Ollama chat")
print("   POST /api/embeddings→ Ollama embeddings")
print("   GET  /api/tags      → List models")

# ══════════════════════════════════════════════════════════════════════════
# CELL 6: Launch Server + Ngrok Tunnel
# ══════════════════════════════════════════════════════════════════════════
 
from pyngrok import ngrok
import time, threading
 
if NGROK_AUTH_TOKEN == "YOUR_NGROK_AUTH_TOKEN":
    print("❌ Cell 3 එකේ Ngrok Token paste කරන්න!")
else:
    PORT = 5050
 
    # Start Flask in background thread
    flask_thread = threading.Thread(
        target=lambda: app.run(
            host        = "0.0.0.0",
            port        = PORT,
            debug       = False,
            use_reloader= False
        ),
        daemon=True
    )
    flask_thread.start()
    time.sleep(3)
 
    # Start ngrok
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    for t in ngrok.get_tunnels():
        ngrok.disconnect(t.public_url)
 
    tunnel = ngrok.connect(PORT)
    URL    = tunnel.public_url
 
    print()
    print("=" * 70)
    print(" 🚔  POLICE AI CLOUD SERVER — LIVE!  🚔 ".center(70))
    print("=" * 70)
    print(f"  🌐  Public URL : {URL}")
    print()
    print(f"  📡  OCR only   : POST  {URL}/gpu-ocr")
    print(f"  🔁  OCR + AI   : POST  {URL}/process          ← USE THIS")
    print(f"  🤖  AI only    : POST  {URL}/api/generate")
    print(f"  💬  Chat       : POST  {URL}/api/chat")
    print(f"  ❤️   Health     : GET   {URL}/health")
    print(f"  📊  Stats      : GET   {URL}/stats")
    print()
    print(f"  Surya OCR : {'✅ Ready  (' + surya_api_version + ')' if SURYA_LOADED else '❌ Failed'}")
    print(f"  Ollama    : ✅ police-ai-master (gemma2:9b)")
    print()
    print("  ── config.json ──────────────────────────────────────────────")
    print(f'  "kaggle_url"     : "{URL}/api/generate"')
    print(f'  "kaggle_ocr_url" : "{URL}/gpu-ocr"')
    print(f'  "kaggle_process_url" : "{URL}/process"')
    print("  ─────────────────────────────────────────────────────────────")
    print()
    print("  ⚠️  මෙම tab එක close නොකරන්න — server stop වෙයි!")
    print("=" * 70)
    print()
 
    # Keep-alive loop with health ping
    n = 0
    while True:
        time.sleep(30)
        n += 1
        mins = n * 30 // 60
 
        # Every 5 min: ping own health endpoint to prevent idle timeout
        if n % 10 == 0:
            try:
                h = _req.get(f"http://localhost:{PORT}/health", timeout=5).json()
                gpu_info = ""
                if torch.cuda.is_available():
                    used = torch.cuda.memory_allocated(0) / 1e9
                    gpu_info = f"| GPU {used:.1f}GB used"
                print(f"  💓 {mins}min running {gpu_info} | {URL}")
            except Exception:
                print(f"  💓 {mins}min running | {URL}")
                