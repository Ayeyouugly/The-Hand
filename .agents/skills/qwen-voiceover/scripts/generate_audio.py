import os
import sys
import json
import re
import tempfile
import shutil
import torch
import numpy as np
import soundfile as sf
import librosa
import ffmpeg
from qwen_tts import Qwen3TTSModel

# ── Paths ──────────────────────────────────────────────────────────────────────
WORKSPACE_DIR    = r"c:/Users/yeabsira/Desktop/THE HAND"
REF_AUDIO_PATH   = os.path.join(WORKSPACE_DIR, "assets", "audio", "my_voice.wav")
REF_TEXT_PATH    = os.path.join(WORKSPACE_DIR, "assets", "audio", "my_voice_script.txt")
JSON_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "orchestration_data", "temporal_callbacks.json")
DEFAULT_OUTPUT   = os.path.join(WORKSPACE_DIR, "assets", "master_voiceover.wav")

# ── REF_TEXT: read strictly from my_voice_script.txt ──────────────────────────
with open(REF_TEXT_PATH, "r", encoding="utf-8") as _f:
    REF_TEXT = _f.read().strip()

print(f"[qwen-voiceover] REF_TEXT loaded ({len(REF_TEXT)} chars) from: {REF_TEXT_PATH}")

# ── Model ──────────────────────────────────────────────────────────────────────
print("[qwen-voiceover] Loading model on cpu (torch.float32)...")
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    device_map="cpu",
    dtype=torch.float32
)

# ── CLI Arguments ──────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python generate_audio.py <script_text_or_file_path> [output_path]")
    sys.exit(1)

script_input = sys.argv[1]
output_path  = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

if os.path.isfile(script_input):
    with open(script_input, "r", encoding="utf-8") as f:
        script_text = f.read()
else:
    script_text = script_input

print(f"[qwen-voiceover] Script loaded ({len(script_text)} chars).")

# ── Semantic Chunking ──────────────────────────────────────────────────────────
chunks = re.split(r'(?<=[.!?])\s+', script_text.strip())
chunks = [c.strip() for c in chunks if c.strip()]
print(f"[qwen-voiceover] {len(chunks)} chunks detected.")

# ── Voice Profile (extracted ONCE before the loop) ────────────────────────────
print("[qwen-voiceover] Loading reference audio...")
ref_audio_data, ref_audio_sr = librosa.load(REF_AUDIO_PATH, sr=24000)
ref_audio_tuple = (ref_audio_data, ref_audio_sr)

print("[qwen-voiceover] Extracting voice clone profile...")
prompt_items = model.create_voice_clone_prompt(
    ref_audio=ref_audio_tuple,
    ref_text=REF_TEXT,
    x_vector_only_mode=False
)
print("[qwen-voiceover] Voice profile ready.")

# ── Synthesis Loop ─────────────────────────────────────────────────────────────
SAMPLE_RATE   = 24000
CROSSFADE_DUR = 0.1  # seconds

tmp_dir = tempfile.mkdtemp(prefix="qwen_chunks_")
chunk_paths = []
timestamps  = []
current_time = 0.0

try:
    for i, chunk in enumerate(chunks):
        print(f"[qwen-voiceover] Synthesizing chunk {i+1}/{len(chunks)}: {chunk[:60]}...")
        audio_list, sr = model.generate_voice_clone(
            text=chunk,
            voice_clone_prompt=prompt_items
        )

        audio = np.array(audio_list[0]).flatten().astype(np.float32)
        duration = float(len(audio)) / float(sr)

        # Save chunk as individual .wav
        chunk_path = os.path.join(tmp_dir, f"chunk_{i:04d}.wav")
        sf.write(chunk_path, audio, SAMPLE_RATE)
        chunk_paths.append(chunk_path)

        # Timestamps: each chunk's perceptual start accounts for the crossfade overlap
        if i == 0:
            start_t = 0.0
            end_t   = duration
        else:
            # The crossfade overlaps the tail of the previous chunk, so the
            # new chunk's audible content starts at (current_time - crossfade_dur)
            start_t = round(current_time - CROSSFADE_DUR, 3)
            end_t   = round(start_t + duration, 3)

        timestamps.append({
            "chunk_index": i,
            "text":        chunk,
            "start_time":  round(float(start_t), 3),
            "end_time":    round(float(end_t),   3)
        })
        current_time = float(end_t)

    # ── Stitching with ffmpeg-python acrossfade=d=0.1 ─────────────────────────
    print(f"[qwen-voiceover] Stitching {len(chunk_paths)} chunks with acrossfade=d={CROSSFADE_DUR}...")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if len(chunk_paths) == 1:
        # Only one chunk — no crossfade needed, just copy it
        shutil.copy(chunk_paths[0], output_path)
    else:
        # Build an ffmpeg acrossfade filter chain
        # Pattern: [a0][a1] acrossfade=d=0.1 [ac0]
        #          [ac0][a2] acrossfade=d=0.1 [ac1]  ...etc
        inputs = [ffmpeg.input(p) for p in chunk_paths]
        stream = inputs[0]
        for j in range(1, len(inputs)):
            stream = ffmpeg.filter(
                [stream, inputs[j]],
                "acrossfade",
                d=CROSSFADE_DUR,
                c1="tri",
                c2="tri"
            )

        out = ffmpeg.output(stream, output_path, ar=SAMPLE_RATE, acodec="pcm_s16le")
        ffmpeg.run(out, overwrite_output=True, quiet=False)

    print(f"[qwen-voiceover] Final audio saved → {output_path}")

    # ── Save Timestamps ────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(timestamps, f, indent=2, ensure_ascii=False)
    print(f"[qwen-voiceover] Timestamps saved → {JSON_OUTPUT_PATH}")

finally:
    # ── Cleanup temporary chunk files ─────────────────────────────────────────
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("[qwen-voiceover] Temporary chunk files cleaned up.")
