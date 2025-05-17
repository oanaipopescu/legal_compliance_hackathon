import os
import re

# Define input and output directories
input_dir = "rdf_output"
output_dir = "rdf_output_fixed"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get all Article_X.ttl files
ttl_files = [f for f in os.listdir(input_dir) if f.startswith("Article_") and f.endswith(".ttl")]

# Process each file
for filename in ttl_files:
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    
    # Read file content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove ```turtle and ``` markers
    # This pattern matches ```turtle at the start and ``` at the end with any content in between
    cleaned_content = re.sub(r'^```turtle\s*|\s*```$', '', content, flags=re.MULTILINE)
    
    # Write cleaned content to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Processed: {filename}")

print(f"\nAll files processed. Cleaned files saved to '{output_dir}/' directory.")