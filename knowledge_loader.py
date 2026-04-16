import json
import os


class ExpertKnowledgeLoader:
    def __init__(self, jsonl_path="dataset/training_data.jsonl"):
        self.jsonl_path = jsonl_path
        self.knowledge = []
        self._load_knowledge()

    def _load_knowledge(self):
        if not os.path.exists(self.jsonl_path):
            print(f"  [Knowledge] ⚠️ Knowledge file not found at {self.jsonl_path}")
            return

        try:
            with open(self.jsonl_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.knowledge.append(json.loads(line))
            print(f"  [Knowledge] ✅ Loaded {len(self.knowledge)} Expert Gold Pairs.")
        except Exception as e:
            print(f"  [Knowledge] ❌ Error loading knowledge: {e}")

    def get_few_shot_context(self, limit=5):
        """Returns a string formatted as few-shot examples for AI instructions."""
        if not self.knowledge:
            return ""

        context = "\n\n### EXPERT REFERENCE EXAMPLES (Sri Lanka Police Standard):\n"
        # Use the most recent/best ones
        examples = self.knowledge[:limit]

        for i, pair in enumerate(examples, 1):
            sinhala = pair.get("sinhala", "").strip()
            english = pair.get("english", "").strip()

            context += f"Example {i}:\n"
            context += f"Sinhala: {sinhala}\n"
            context += f"Standard English: {english}\n"
            context += "-" * 20 + "\n"

        return context

if __name__ == "__main__":
    loader = ExpertKnowledgeLoader()
    print(loader.get_few_shot_context(limit=2))
