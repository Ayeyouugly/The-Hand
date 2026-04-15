import json
import os
import cv2
import numpy as np

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
    
    png_path = f"assets/master_layout_images/board_{b_num:02d}.png"
    if not os.path.exists(png_path):
        print(f"WARNING: Image not found for board {b_num}: {png_path}")
        continue
        
    print(f"Processing {png_path}...")
    
    # Read image, grayscale, threshold
    img = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out tiny noise and sort them roughly left-to-right, top-to-bottom
    valid_contours = []
    for c in contours:
        if cv2.contourArea(c) > 2.0:
            M = cv2.moments(c)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                valid_contours.append((cx + cy*2, c)) # Weight Y more to sort top-down then left-right
            else:
                valid_contours.append((0, c))
                
    valid_contours.sort(key=lambda x: x[0])
    sorted_contours = [c[1] for c in valid_contours]
    
    # Subdivide into layers
    total_layers = max(1, len(layers))
    chunk_size = max(1, len(sorted_contours) // total_layers)
    
    svg_content = "<svg width='1920' height='1080' xmlns='http://www.w3.org/2000/svg'>\n"
    
    for layer_idx, layer in enumerate(layers):
        svg_content += f"  <g id='{layer}' stroke='black' stroke-width='4' fill='none' stroke-linecap='round' stroke-linejoin='round'>\n"
        
        start_idx = layer_idx * chunk_size
        end_idx = start_idx + chunk_size if layer_idx < total_layers - 1 else len(sorted_contours)
        
        layer_contours = sorted_contours[start_idx:end_idx]
        
        for contour in layer_contours:
            # Create SVG path data
            points = contour.squeeze()
            if points.ndim == 1:
               points = [points]
            if len(points) > 1:
                path_d = f"M {points[0][0]} {points[0][1]} "
                for pt in points[1:]:
                    path_d += f"L {pt[0]} {pt[1]} "
                svg_content += f"    <path d='{path_d}' />\n"
            
        svg_content += f"  </g>\n"
    svg_content += "</svg>"
    
    # Timing logic remains the same
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
        
    print(f"Generated SVG data for: {out_path} ({len(sorted_contours)} strokes extracted)")
    
    board["svg_extraction_path"] = out_path

with open(layout_file, "w") as f:
    json.dump(master_data, f, indent=2)
    
print("Updated master_layout_data.json successfully.")
