import json

nb = {
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# 🚔 Sri Lanka Police AI - Master Training & serving (Gemma-2-9B)\n",
        "\n",
        "මෙම Notebook එකෙන් **Gemma-2-9B** model එක fine-tune කර සෘජුවම සේවා ලබාගත හැක.\n",
        "\n",
        "### පියවර:\n",
        "1. **Settings**: Internet ON, **GPU T4 x2** select කරන්න.\n",
        "2. **Dataset**: `nakigani/police-ai-dataset` දැනටමත් සම්බන්ධ කර ඇත.\n",
        "3. **Run All** ඔබන්න."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": { "trusted": True },
      "source": [
        "# Cell 1: Install Extended Dependencies\n",
        "!pip install --quiet unsloth surya-ocr Pillow flask pyngrok \"transformers<5.0.0\"\n",
        "!pip install --quiet --upgrade --force-reinstall Pillow\n",
        "!sudo apt-get install -y zstd > /dev/null 2>&1\n",
        "!curl -fsSL https://ollama.com/install.sh | sh\n",
        "import numpy as np\n",
        "import torch\n",
        "print(f\"✅ NumPy: {np.__version__} | ✅ CUDA: {torch.cuda.is_available()}\")"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": { "trusted": True },
      "source": [
        "# Cell 2: Fine-Tuning with Robust Path Discovery\n",
        "import os, glob\n",
        "TRAIN_DATA_SEARCH = glob.glob(\"/kaggle/input/**/training_data.jsonl\", recursive=True)\n",
        "if TRAIN_DATA_SEARCH:\n",
        "    TRAIN_DATA = TRAIN_DATA_SEARCH[0]\n",
        "    print(f\"🧠 [Training] Data found at: {TRAIN_DATA}\")\n",
        "    from unsloth import FastLanguageModel\n",
        "    from trl import SFTTrainer\n",
        "    from transformers import TrainingArguments\n",
        "    from datasets import load_dataset\n",
        "    \n",
        "    model, tokenizer = FastLanguageModel.from_pretrained(\n",
        "        model_name = \"unsloth/gemma-2-9b-it-bnb-4bit\",\n",
        "        max_seq_length = 2048, load_in_4bit = True,\n",
        "    )\n",
        "    model = FastLanguageModel.get_peft_model(\n",
        "        model, r = 32, \n",
        "        target_modules = [\"q_proj\", \"k_proj\", \"v_proj\", \"o_proj\", \"gate_proj\", \"up_proj\", \"down_proj\"],\n",
        "        lora_alpha = 16, lora_dropout = 0, bias = \"none\",\n",
        "        use_gradient_checkpointing = \"unsloth\", random_state = 3407,\n",
        "    )\n",
        "    \n",
        "    dataset = load_dataset(\"json\", data_files=TRAIN_DATA, split=\"train\")\n",
        "    def formatting_prompts_func(examples):\n",
        "        convos = examples[\"messages\"]\n",
        "        return { \"text\" : [tokenizer.apply_chat_template(c, tokenize=False) for c in convos] }\n",
        "    dataset = dataset.map(formatting_prompts_func, batched=True)\n",
        "    \n",
        "    trainer = SFTTrainer(\n",
        "        model=model, tokenizer=tokenizer, train_dataset=dataset,\n",
        "        dataset_text_field=\"text\", max_seq_length=2048,\n",
        "        args=TrainingArguments(\n",
        "            per_device_train_batch_size=2, gradient_accumulation_steps=4,\n",
        "            max_steps=60, learning_rate=2e-4, fp16=True, logging_steps=1,\n",
        "            output_dir=\"output\", optim=\"adamw_8bit\",\n",
        "        ),\n",
        "    )\n",
        "    trainer.train()\n",
        "    print(\"📦 [Export] Saving to GGUF...\")\n",
        "    model.save_pretrained_gguf(\"police-ai-master-gguf\", tokenizer, quantization_method = \"q4_k_m\")\n",
        "    print(\"✅ Training Complete!\")\n",
        "else:\n",
        "    print(\"⚠️ [Skip] Training data not found. Check dataset attachment.\")"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": { "trusted": True },
      "source": [
        "# Cell 3: Setup Ollama & servent\n",
        "import subprocess, time\n",
        "subprocess.Popen([\"ollama\", \"serve\"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n",
        "time.sleep(10)\n",
        "\n",
        "if os.path.exists(\"police-ai-master-gguf/unsloth.Q4_K_M.gguf\"):\n",
        "    print(\"🔥 Using FAST FINE-TUNED GGUF Model!\")\n",
        "    with open(\"Modelfile\", \"w\") as f:\n",
        "        f.write(\"FROM ./police-ai-master-gguf/unsloth.Q4_K_M.gguf\\n\")\n",
        "        f.write(\"PARAMETER temperature 0.05\\n\")\n",
        "        f.write(\"SYSTEM \\\"You are the Sri Lanka Police AI (Gemma Architecture). Use institutional terminology.\\\"\\n\")\n",
        "    !ollama create police-ai-master -f Modelfile\n",
        "else:\n",
        "    print(\"🚜 Using Base Model\")\n",
        "    !ollama pull gemma2:9b\n",
        "    !ollama create police-ai-master -b gemma2:9b"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": { "trusted": True },
      "source": [
        "# Cell 4: Start Tunnel (Random URL to avoid conflicts)\n",
        "NGROK_AUTH_TOKEN = \"3C0C7gFkX4IQuTy2cMMPHYznbNh_4CZ5YG6ekExX6sBKNfhpv\"\n",
        "from pyngrok import ngrok\n",
        "ngrok.set_auth_token(NGROK_AUTH_TOKEN)\n",
        "for t in ngrok.get_tunnels(): ngrok.disconnect(t.public_url)\n",
        "# Use connect(5050) without a static domain to get a unique random one\n",
        "url = ngrok.connect(5050).public_url\n",
        "print(f\"\\n🔥 GEMMA PUBLIC URL: {url}\")"
      ]
    }
  ],
  "metadata": {
    "kernelspec": { "display_name": "Python 3", "name": "python3" },
    "language_info": { "name": "python" }
  },
  "nbformat": 4, "nbformat_minor": 4
}

target_path = r"d:\PROJECTS\pdf convert tool\Kaggle_Police_AI_v2.ipynb"
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
print(f"Successfully generated hardened Gemma notebook at {target_path}")
