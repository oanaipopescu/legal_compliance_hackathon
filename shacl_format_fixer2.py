import os
import re

# Directories
INPUT_FOLDER = "shacl_output_fixed"
OUTPUT_FOLDER = "shacl_output_fixed"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Process each file
for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".ttl"):
        continue
    
    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix regex patterns: replace \d with \\d
    # Using string concatenation instead of f-string to handle backslashes
    fixed_content = re.sub(r'sh:pattern\s+"([^"]*\\d[^"]*)"', 
                          lambda m: 'sh:pattern "' + m.group(1).replace("\\d", "\\\\d") + '"', 
                          content)
    
    # Fix any other potentially problematic regex escape sequences
    escape_chars = ['w', 's', 'b', 'D', 'W', 'S']
    for escape_char in escape_chars:
        fixed_content = fixed_content.replace(f'"\\{escape_char}', f'"\\\\{escape_char}')
    
    # Write the fixed file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    # If we made changes, note it
    if fixed_content != content:
        print(f"Fixed regex in: {filename}")
    else:
        print(f"No changes needed for: {filename}")

print(f"\nAll files processed. Fixed files saved to '{OUTPUT_FOLDER}'")