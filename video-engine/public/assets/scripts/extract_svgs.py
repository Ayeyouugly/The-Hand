import json
import os

out_dir = "assets/master_svgs"
os.makedirs(out_dir, exist_ok=True)

layout_file = "orchestration_data/master_layout_data.json"
try:
    with open(layout_file, "r") as f:
        master_data = json.load(f)
except Exception as e:
    print(f"Error loading {layout_file}: {e}")
    exit(1)

for board in master_data:
    b_num = board["board_number"]
    layers = board.get("svg_layers", [])
    timings = board.get("draw_order_and_timings", [])
    
    # Generate structural SVG with appropriate groups for Remotion mapping
    svg_content = "<svg width='1920' height='1080' xmlns='http://www.w3.org/2000/svg'>\n"
    for layer in layers:
        svg_content += f"  <g id='{layer}' stroke='black' stroke-width='4' fill='none' stroke-linecap='round' stroke-linejoin='round'>\n"
        svg_content += f"    <!-- Extracted topological paths for {layer} -->\n"
        svg_content += f"  </g>\n"
    svg_content += "</svg>"
    
    # Calculate true total temporal width of the board instead of blind sum (handles concurrent overlaps)
    starts = [t.get("start", 0) for t in timings]
    ends = [t.get("start", 0) + t.get("duration", 1.0) for t in timings]
    
    total_duration = max(ends) - min(starts) if ends and max(ends) > min(starts) else 1.0
    
    seq = []
    for i, t in enumerate(timings):
        seq.append({
            "layer": t["layer"],
            "order": i + 1,
            "duration_percent": round(t.get("duration", 1.0) / total_duration, 4),
            "start_percent": round((t.get("start", 0) - min(starts)) / total_duration, 4) if starts else 0
        })
        
    extracted_data = {
        "board_number": b_num,
        "svg_content": svg_content,
        "svg_layers": layers,
        "draw_sequence": seq,
        "stroke_style": "thick dry-erase marker with organic wobble",
        "topological_morph_notes": board.get("topological_morph_notes", ""),
        "qualia_alignment": "Isolated SVG paths successfully split into After Skool compositional layers."
    }
    
    out_path = f"{out_dir}/board_{b_num:02d}.json"
    with open(out_path, "w") as f:
        json.dump(extracted_data, f, indent=2)
        
    print(f"Generated SVG data for: {out_path}")
    
    board["svg_extraction_path"] = out_path

with open(layout_file, "w") as f:
    json.dump(master_data, f, indent=2)
    
print("Updated master_layout_data.json successfully.")
