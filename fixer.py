import re

# File path
file_path = "policy_rdf_output_fixed/Section_3_7.ttl"
output_path = "policy_rdf_output_fixed/Section_3_7.ttl"

# Read the content
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 1. Fix the xsd:duration values - convert to ISO 8601 duration format
# "72 hours" -> "PT72H", "5 days" -> "P5D", "2 days" -> "P2D"
content = content.replace('"72 hours"^^xsd:duration', '"PT72H"^^xsd:duration')
content = content.replace('"5 days"^^xsd:duration', '"P5D"^^xsd:duration')
content = content.replace('"2 days"^^xsd:duration', '"P2D"^^xsd:duration')

# 2. Fix the syntax error with RegulationRule :rule1
content = content.replace(':RegulationRule :rule1 a', ':rule1 a')

# Write the fixed content
with open(output_path, 'w', encoding='utf-8') as file:
    file.write(content)

print(f"Fixed the duration formats and syntax in {output_path}")