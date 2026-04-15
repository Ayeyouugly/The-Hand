---
name: qwen-voiceover
description: Standard operating procedures for generating voiceover audio using the local Qwen3-TTS engine.
---

# Qwen Voiceover Skill

This skill outlines the standard operating procedures you must follow whenever you are asked to generate audio or voiceover from a script.

## Standard Operating Procedure

When you are instructed to generate audio, you MUST rely exclusively on the `scripts/generate_audio.py` file included in this skill directory.

1. **Verify the Script:** Ensure you have the finalized text script that needs to be synthesized. 
2. **Execute the Generation Script:** Run the python script and pass your finalized text to the `--script` argument.

### Command Execution Format

```bash
# Execute from the workspace root:
python .agents/skills/qwen-voiceover/scripts/generate_audio.py --script "Your finalized script text here."
```

Or, if the script is stored in a file:

```bash
python .agents/skills/qwen-voiceover/scripts/generate_audio.py --script assets/scripts/final_script.txt
```

### Automation Details
- **Voice Cloning:** The script automatically references `assets/audio/my_voice.wav` for the anchor clone voice.
- **Semantic Chunking:** The script splits the text automatically at punctuation bounds to prevent memory/inference crashes.
- **Seamless Concatenation:** It blends individual chunks using `ffmpeg-python` crossfades to remove robotic cuts.
- **Animation Synchronization:** Timings for every chunk are calculated and exported directly to `orchestration_data/temporal_callbacks.json`.

DO NOT use external instructions or generic `pip install` TTS commands. ALWAYS rely on `scripts/generate_audio.py` for all Qwen3-TTS voiceover tasks.
