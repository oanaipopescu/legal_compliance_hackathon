import os
import re

# === Configuration ===
input_file = "translated_regulations/greek.txt"
output_folder = "greek_articles"

# === Ensure output directory exists ===
os.makedirs(output_folder, exist_ok=True)

# === Read full text from file ===
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# === Regex to match 'Article [number]' ===
article_header_regex = re.compile(r'\bArticle\s+(\d+)\b', re.IGNORECASE)

# === Identify all candidate matches ===
matches = list(article_header_regex.finditer(content))

# === Filter only sequential articles ===
valid_articles = []
last_number = None

for match in matches:
    number = int(match.group(1))
    if last_number is None or number == last_number + 1:
        valid_articles.append((number, match.start()))
        last_number = number
    else:
        # Not sequential — likely a mid-paragraph reference
        continue

# === Extract and save content between valid articles ===
for i in range(len(valid_articles)):
    number, start = valid_articles[i]
    end = valid_articles[i + 1][1] if i + 1 < len(valid_articles) else len(content)
    article_text = content[start:end].strip()

    filename = f"Article_{number}.txt"
    filepath = os.path.join(output_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article_text)

    print(f"✅ Saved {filename} ({end - start} chars)")

print(f"\n✅ Done! Extracted {len(valid_articles)} articles to '{output_folder}/'")