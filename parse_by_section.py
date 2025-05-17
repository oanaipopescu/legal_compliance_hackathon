import os
import re

# === Configuration ===
input_file = "policy.txt"
output_folder = "policy_sections"

# === Ensure output directory exists ===
os.makedirs(output_folder, exist_ok=True)

# === Read full text from file ===
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# === Regex to match section headers (e.g. "1 Introduction", "2.3 Reporting", etc.)
section_header_regex = re.compile(
    r'^(?P<sec>(\d+(\.\d+)*))\s+([^\n]+)',  # matches section numbers + title
    re.MULTILINE
)

# === Identify all section headers ===
matches = list(section_header_regex.finditer(content))

# === Extract and save each section ===
for i in range(len(matches)):
    match = matches[i]
    section_number = match.group('sec').replace('.', '_')  # use underscores in filenames
    start = match.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

    section_text = content[start:end].strip()
    filename = f"Section_{section_number}.txt"
    filepath = os.path.join(output_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(section_text)

    print(f"✅ Saved {filename} ({end - start} chars)")

print(f"\n✅ Done! Extracted {len(matches)} sections to '{output_folder}/'")
