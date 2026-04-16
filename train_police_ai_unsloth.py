import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel

# Configuration
MODEL_NAME = "unsloth/gemma-2-9b-it-bnb-4bit" # Base model
DATASET_PATH = "dataset/training_data.jsonl"
OUTPUT_DIR = "police-ai-trained"
MAX_SEQ_LENGTH = 2048
LORA_RANK = 32

# Mapping to ensure institutional terminology consistency
INSTITUTIONAL_CATEGORIES = {
    "04": "SERIOUS CRIMES COMMITTED",
    "09": "RAPE, SEXUAL ABUSE & CHILD ABUSE",
    "10": "FATAL ACCIDENTS",
    "28": "OTHER MATTERS"
}

def train():
    print("🚀 [Training] Starting Master Police AI Fine-tuning...")

    # 1. Load Model and Tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = MODEL_NAME,
        max_seq_length = MAX_SEQ_LENGTH,
        load_in_4bit = True,
    )

    # 2. Add LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r = LORA_RANK,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                         "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
    )

    # 3. Load Dataset
    def formatting_prompts_func(examples):
        convos = examples["messages"]
        texts = []
        for convo in convos:
            # Format using standard ChatML or Gemma template
            text = tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False)
            texts.append(text)
        return { "text" : texts, }

    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    dataset = dataset.map(formatting_prompts_func, batched=True)

    # 4. Trainer
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = MAX_SEQ_LENGTH,
        dataset_num_proc = 2,
        packing = False,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60, # Small dataset, small steps
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = OUTPUT_DIR,
        ),
    )

    # 5. Execute Training
    print("🧠 [Training] Executing iterations...")
    trainer.train()

    # 6. Export to GGUF
    print("📦 [Export] Saving to GGUF format for Ollama...")
    model.save_pretrained_gguf(
        "police-ai-master-gguf",
        tokenizer,
        quantization_method = "q4_k_m"
    )

    print("✅ [Success] Fine-tuning complete! 'police-ai-master-gguf' is ready.")

if __name__ == "__main__":
    train()
