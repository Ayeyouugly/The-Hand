import json
import glob

files = sorted(glob.glob('assets/master_svgs/board_*.json'))
all_ok = True

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
        b_num = data.get('board_number')
        print(f"\n--- Board {b_num} ---")
        
        # Check Stroke Quality
        style = data.get('stroke_style', '').lower()
        if 'thick' not in style or 'wobble' not in style:
            print("ISSUE: Stroke style does not match After Skool (thick marker with organic wobble).")
            all_ok = False
        else:
            print("Stroke Quality: OK")
        
        # Check Layers and Draw Order
        layers = data.get('svg_layers', [])
        seq = data.get('draw_sequence', [])
        if len(layers) != len(seq):
            print(f"ISSUE: Number of layers ({len(layers)}) does not match draw sequence ({len(seq)}).")
            all_ok = False
        else:
            # Check if all layers in seq match the layers array in some order
            seq_layers = [s.get('layer') for s in seq]
            if set(layers) != set(seq_layers):
                 print("ISSUE: Layer names in sequence do not perfectly match defined svg_layers.")
                 all_ok = False
            else:
                 print("Layers & Draw Order Alignment: OK")
            
        # Check Topological Continuity
        morph = data.get('topological_morph_notes', '')
        if not morph and b_num != 7: # Board 7 is outro, may not have next morph
            print("ISSUE: Missing topological continuity notes.")
            all_ok = False
        else:
            print("Topological Continuity: OK")

if all_ok:
    print("\n[VERIFICATION COMPLETE: ALL SVG DATA PACKAGES ARE FULLY ALIGNED WITH STYLE BIBLE]")
else:
    print("\n[VERIFICATION FAILED: ISSUES FOUND. Saye intervention required.]")
