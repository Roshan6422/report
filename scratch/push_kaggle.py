import json
import os
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi

# Paths
BASE_DIR = r"d:\PROJECTS\pdf convert tool"
DEPLOY_DIR = os.path.join(BASE_DIR, "kaggle_deploy_v2.1")
NB_SOURCE = os.path.join(BASE_DIR, "Kaggle_Police_AI_v2.1.ipynb")
NB_TARGET = os.path.join(DEPLOY_DIR, "Kaggle_Police_AI_v2.1.ipynb")
META_PATH = os.path.join(DEPLOY_DIR, "kernel-metadata.json")

# 1. Aggressive ASCII Encoding for Notebook
# This bypasses the Windows cp1252/utf-8 mismatch in Kaggle library
with open(NB_SOURCE, "r", encoding="utf-8") as f:
    nb_data = json.load(f)

# Use ensure_ascii=True to convert all non-ASCII to \uXXXX
ascii_nb_json = json.dumps(nb_data, ensure_ascii=True, indent=2)

if not os.path.exists(DEPLOY_DIR):
    os.makedirs(DEPLOY_DIR)

with open(NB_TARGET, "w", encoding="ascii") as f:
    f.write(ascii_nb_json)

# 2. Create Metadata (Targeting EXISTING kernel ID to avoid 401 on creation)
metadata = {
    "id": "nakigani/police-ai-master-training",
    "title": "Police AI Master Setup v2.2",
    "code_file": "Kaggle_Police_AI_v2.1.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": True,
    "enable_tpu": False,
    "enable_internet": True,
    "dataset_sources": ["nakigani/police-ai-dataset"],
    "model_sources": [],
    "competition_sources": [],
    "kernel_sources": []
}

with open(META_PATH, "w", encoding="ascii") as f:
    json.dump(metadata, f, indent=4)

# 3. Authenticate and Push
os.environ["PYTHONUTF8"] = "1"
api = KaggleApi()
api.authenticate()
print(f"Pushing Master Setup to Kaggle ID: {metadata['id']}...")
api.kernels_push(DEPLOY_DIR)
print("SUCCESS: Kernel pushed to Kaggle!")
