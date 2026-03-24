import json
import os
import re

def process_notebook(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    file_name = os.path.basename(file_path)
    
    mapping = {
        "1. ingest_circuits_file.ipynb": ("circuits.csv", "csv"),
        "2. ingest_races_file.ipynb": ("races.csv", "csv"),
        "3. ingest_constructors_file.ipynb": ("constructors.json", "json"),
        "4. ingest_drivers_file.ipynb": ("drivers.json", "json"),
        "5. ingest_results_file.ipynb": ("results.json", "json"),
        "6. ingest_pitstops_file.ipynb": ("pit_stops.json", "json"),
        "7. ingest_laptimes_files.ipynb": ("lap_times directory csv", "csv"),
        "8. ingest_qualifying_files.ipynb": ("qualifying directory json", "json")
    }
    
    target_name, file_format = mapping.get(file_name, ("unknown", "unknown"))
    
    new_cells = []
    step1_emitted = False
    step2_emitted = False
    step3_emitted = False
    is_first_header = True
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            source_lines = cell['source']
            new_source_lines = []
            
            # Combine to check for header status but process line by line for bolding
            full_source = "".join(source_lines)
            
            if full_source.strip().startswith("#"):
                # Main Header: First header in the notebook
                if is_first_header:
                    new_source_lines = [f"## Ingest {target_name}\n"]
                    is_first_header = False
                
                # Special for Notebook 1
                elif file_name == "1. ingest_circuits_file.ipynb" and "Why inferSchema" in full_source:
                    for line in source_lines:
                        if line.strip().startswith("#"):
                            line = f"**{line.replace('#', '').strip()}**\n"
                        new_source_lines.append(line)
                
                # Step 1
                elif ("Step 1" in full_source or "Read" in full_source or "Ingest" in full_source) and not any(x in full_source for x in ["1.1", "1.2"]) and not step1_emitted:
                    new_source_lines = [f"### Step 1 - Read the {file_format} file\n"]
                    step1_emitted = True
                
                # Step 1.1
                elif "1.1" in full_source or "Define" in full_source:
                    new_source_lines = ["#### 1.1 Define the schema\n"]
                
                # Step 1.2
                elif "1.2" in full_source or ("Read" in full_source and step1_emitted):
                    new_source_lines = [f"#### 1.2 Read the {file_format} file\n"]
                
                # Step 2
                elif ("Step 2" in full_source or "Transform" in full_source or "Rename" in full_source or "Select" in full_source or "Add" in full_source or "Drop" in full_source):
                    if not step2_emitted:
                        new_source_lines = ["### Step 2 - Transform the data\n"]
                        step2_emitted = True
                    else:
                        continue # Skip cell
                
                # Step 3
                elif ("Step 3" in full_source or "Step 4" in full_source or "Step 5" in full_source) and "Write" in full_source:
                    if not step3_emitted:
                        new_source_lines = ["### Step 3 - Write the output to parquet\n"]
                        step3_emitted = True
                    else:
                        continue # Skip cell
            else:
                # Process non-header markdown cells for typos
                for line in source_lines:
                    line = line.replace("📝", "")
                    line = re.sub(r'[^\x00-\x7f]', '', line)
                    line = line.replace("Difine", "Define").replace("unwated", "unwanted").replace("directoy", "directory")
                    new_source_lines.append(line)
            
            if not new_source_lines:
                continue
            cell['source'] = new_source_lines
        
        new_cells.append(cell)

    nb['cells'] = new_cells
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

files = [
    "ingestion/1. ingest_circuits_file.ipynb",
    "ingestion/2. ingest_races_file.ipynb",
    "ingestion/3. ingest_constructors_file.ipynb",
    "ingestion/4. ingest_drivers_file.ipynb",
    "ingestion/5. ingest_results_file.ipynb",
    "ingestion/6. ingest_pitstops_file.ipynb",
    "ingestion/7. ingest_laptimes_files.ipynb",
    "ingestion/8. ingest_qualifying_files.ipynb"
]

for f in files:
    process_notebook(f)
    print(f"Processed {f}")
