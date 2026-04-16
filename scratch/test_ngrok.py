import os
import sys
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

from ai_engine_manager import AIEngineManager


def test_ngrok_headers():
    print("--- Testing Ngrok Header Injection ---")

    # Mocking config.json
    mock_config = {
        "ai_engines": {
            "ollama": {
                "kaggle_url": "https://test-ngrok-link.ngrok-free.app/api/generate",
                "prefer_kaggle": True,
                "kaggle_model": "test-model"
            }
        }
    }

    with patch("builtins.open", MagicMock()):
        with patch("json.load", return_value=mock_config):
            with patch("os.path.isfile", return_value=True):
                mgr = AIEngineManager()
                print(f"Prefer Kaggle: {mgr.prefer_kaggle_ollama}")
                print(f"Kaggle URL: {mgr.kaggle_ollama_url}")

                # Mock requests.post
                with patch("requests.post") as mock_post:
                    mock_res = MagicMock()
                    mock_res.status_code = 200
                    mock_res.json.return_value = {"response": "Test Response"}
                    mock_post.return_value = mock_res

                    mgr.call_ai("Translate this")

                    # Verify headers
                    args, kwargs = mock_post.call_args
                    headers = kwargs.get("headers", {})
                    print(f"Headers sent: {headers}")

                    if headers.get("ngrok-skip-browser-warning") == "true":
                        print("✅ SUCCESS: Ngrok header found!")
                    else:
                        print("❌ FAILURE: Ngrok header missing!")

if __name__ == "__main__":
    test_ngrok_headers()
