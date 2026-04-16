import json

nb_path = r"d:\PROJECTS\pdf convert tool\Kaggle_Police_AI_v2.1.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

# Remove emojis that cause encoding issues on Windows CLI
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            line = line.replace("🔥", "!!").replace("💓", "Alive").replace("✅", "[OK]").replace("🚀", "[GO]").replace("🧠", "[AI]").replace("📦", "[SAVING]").replace("🚜", "[FALLBACK]").replace("🚔", "[POLICE]")
            new_source.append(line)
        cell["source"] = new_source
    elif cell["cell_type"] == "markdown":
        new_source = []
        for line in cell["source"]:
             line = line.replace("🚔", "[POLICE]").replace("⚙️", "[SETTINGS]")
             new_source.append(line)
        cell["source"] = new_source

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("Notebook cleaned of emojis and saved as UTF-8.")
