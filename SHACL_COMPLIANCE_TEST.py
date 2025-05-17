import os
from rdflib import Graph
from pyshacl import validate

# === Configuration ===
POLICY_FOLDER = "policy_rdf_output_fixed"
SHACL_FOLDER = "shacl_output_fixed"
REPORT_FOLDER = "compliance_reports"
SUMMARY_FILE = "compliance_summary.txt"

# === Ensure report folder exists ===
os.makedirs(REPORT_FOLDER, exist_ok=True)

# === Get files ===
policy_files = sorted([f for f in os.listdir(POLICY_FOLDER) if f.endswith(".ttl")])
shacl_files = sorted([f for f in os.listdir(SHACL_FOLDER) if f.endswith(".ttl")])

# === Track overall results ===
summary_lines = []

# === Check each policy section against each SHACL article ===
for policy_file in policy_files:
    policy_path = os.path.join(POLICY_FOLDER, policy_file)
    policy_graph = Graph()
    policy_graph.parse(policy_path, format="turtle")

    for shacl_file in shacl_files:
        shacl_path = os.path.join(SHACL_FOLDER, shacl_file)
        shacl_graph = Graph()
        shacl_graph.parse(shacl_path, format="turtle")

        conforms, report_graph, report_text = validate(
            data_graph=policy_graph,
            shacl_graph=shacl_graph,
            inference='rdfs',
            debug=False
        )

        base_policy = policy_file.replace(".ttl", "")
        base_shacl = shacl_file.replace(".ttl", "")
        result_label = "✅ COMPLIANT" if conforms else "❌ NON-COMPLIANT"
        summary_line = f"{base_policy} vs {base_shacl}: {result_label}"
        summary_lines.append(summary_line)

        # Save detailed report
        report_filename = f"{base_policy}__VS__{base_shacl}.txt"
        report_path = os.path.join(REPORT_FOLDER, report_filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("Conforms: " + str(conforms) + "\n\n")
            f.write(report_text)

        print(f"{summary_line}")

# === Write overall summary file ===
with open(os.path.join(REPORT_FOLDER, SUMMARY_FILE), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print("\n🎉 Compliance checking complete. Summary saved to:", os.path.join(REPORT_FOLDER, SUMMARY_FILE))
