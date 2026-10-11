import time
import os
import platform

# Handle the import based on the operating system and DLL availability
try:
    import fluidsynth
except ImportError as e:
    print(f"Error loading FluidSynth: {e}")
    print("\n--- Troubleshooting ---")
    print("If you are on Windows, ensure that the FluidSynth DLLs (e.g., libfluidsynth.dll)")
    print("are in the root directory of your project or in your system's PATH.")
    exit(1)

def test_audio():
    # 1. Path to the SoundFont file
    # Adjust this path if your assets folder is located elsewhere relative to where you run the script
    sf2_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'FluidR3_GM.sf2')
    
    if not os.path.exists(sf2_path):
        print(f"Error: SoundFont file not found at: {sf2_path}")
        print("Make sure 'FluidR3_GM.sf2' is inside the 'assets' folder.")
        return

    print("Initializing FluidSynth...")
    
    # 2. Initialize the Synthesizer
    fs = fluidsynth.Synth()
    
    # Choose the audio driver based on the OS for lowest latency
    # For Windows: 'dsound' (DirectSound) or 'wasapi'
    # For Mac: 'coreaudio'
    # For Linux: 'alsa' or 'pulseaudio'
    driver = 'dsound' if platform.system() == 'Windows' else 'coreaudio'
    
    try:
        fs.start(driver=driver)
    except Exception as e:
        print(f"Failed to start audio driver '{driver}'. Trying default. Error: {e}")
        fs.start()

    # 3. Load the SoundFont
    print(f"Loading SoundFont: {sf2_path}")
    sfid = fs.sfload(sf2_path)

    # 4. Select the Instrument
    # In General MIDI (GM), Acoustic Bass is usually Program 32
    # Channel 0, SoundFont ID, Bank 0, Program 32
    channel = 0
    program_acoustic_bass = 32 
    fs.program_select(channel, sfid, 0, program_acoustic_bass)

    print("\nPlaying E Blues Arpeggio (Acoustic Bass)...")
    
    # 5. Play some notes (E, G, B, D - an E7 chord arpeggio)
    # Note numbers are standard MIDI notes (E2 = 40)
    velocity = 100 # How hard the string is plucked (0-127)
    
    notes_to_play = [40, 43, 47, 50] # E, G, B, D
    
    for note in notes_to_play:
        print(f"Note On: {note}")
        fs.noteon(channel, note, velocity)
        time.sleep(0.5) # Wait half a second
        fs.noteoff(channel, note)
        
    print("\nTest complete! Cleaning up...")
    
    # 6. Cleanup
    time.sleep(1) # Wait a bit for the last note to decay
    fs.delete()

if __name__ == "__main__":
    test_audio()