import traceback
try:
    import librosa
    REF_AUDIO = r"c:/Users/yeabsira/Desktop/THE HAND/assets/audio/my_voice.wav"
    print("Loading...")
    data, sr = librosa.load(REF_AUDIO, sr=24000)
    print("Success. shape:", data.shape, "sr:", sr)
except Exception as e:
    print("FAILED!")
    traceback.print_exc()
