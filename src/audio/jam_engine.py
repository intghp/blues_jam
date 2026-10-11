import time
import os
import platform
import threading

try:
    import fluidsynth
except ImportError:
    print("FluidSynth not found.")
    exit(1)

from src.core.music_theory import CHROMATIC_SCALE

class JamEngine:
    def __init__(self):
        self.fs = fluidsynth.Synth()
        
        # Audio driver selection based on OS
        driver = 'dsound' if platform.system() == 'Windows' else 'coreaudio'
        try:
            self.fs.start(driver=driver)
        except:
            self.fs.start() # Fallback to default
            
        # Load SoundFont
        sf2_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'FluidR3_GM.sf2')
        self.sfid = self.fs.sfload(sf2_path)
        
        # Setup Channels
        self.BASS_CH = 0
        self.DRUM_CH = 9 # In MIDI, Channel 9 (0-indexed) is strictly for Drums
        
        # Select Acoustic Bass (Bank 0, Program 32) on Channel 0
        self.fs.program_select(self.BASS_CH, self.sfid, 0, 32)
        
        # EXPLICIT FIX: Select Standard Drum Kit (Bank 128, Program 0) on Channel 9
        self.fs.program_select(self.DRUM_CH, self.sfid, 128, 0)
        
        # State control
        self.is_playing = False
        self.play_thread = None

    def get_midi_root(self, note_name: str) -> int:
        """Calculates a low MIDI note number for the bass based on the root note."""
        # MIDI note 36 is C2. We want our bass to be in the octave C2-B2 (MIDI 36-47)
        base_c2_midi = 36
        note_index = CHROMATIC_SCALE.index(note_name.upper())
        return base_c2_midi + note_index

    def play_blues(self, root_note: str, bpm: int = 120):
        """Starts the Jam Session in a separate thread to avoid freezing the UI."""
        if self.is_playing:
            self.stop()
            
        self.is_playing = True
        # Create and start a background thread for the music loop
        self.play_thread = threading.Thread(target=self._jam_loop, args=(root_note, bpm))
        self.play_thread.daemon = True # Thread closes when main program closes
        self.play_thread.start()

    def stop(self):
        """Stops the playback."""
        self.is_playing = False
        if self.play_thread:
            self.play_thread.join(timeout=1.0)
            
        # Turn off all notes to prevent ringing
        for i in range(128):
            self.fs.noteoff(self.BASS_CH, i)
            self.fs.noteoff(self.DRUM_CH, i)

    def _jam_loop(self, root_note: str, bpm: int):
        """The core mathematical loop generating the 12-Bar Blues in real-time."""
        
        # Calculate time (in seconds) for a single quarter note beat
        beat_duration = 60.0 / bpm
        
        root_midi = self.get_midi_root(root_note)
        
        # Standard 12-Bar Blues Progression (Degrees: I, IV, V)
        # We store the distance in semitones from the root (I = 0, IV = 5, V = 7)
        progression = [
            0, 0, 0, 0, # Bars 1-4: I (Root)
            5, 5,       # Bars 5-6: IV (Subdominant)
            0, 0,       # Bars 7-8: I (Root)
            7, 5,       # Bars 9-10: V - IV (Dominant to Subdominant turnaround)
            0, 7        # Bars 11-12: I - V (Turnaround back to start)
        ]
        
        # Drum MIDI Notes mapping
        kick = 36
        ride = 51
        snare = 38
        
        bar_count = 0
        
        print(f"\nJamming in {root_note} at {bpm} BPM...")
        
        while self.is_playing:
            # 1. Determine which chord we are on in the 12-bar form
            current_bar = bar_count % 12
            chord_interval = progression[current_bar]
            current_bass_note = root_midi + chord_interval
            
            # Print current bar for debugging
            chord_name = "I" if chord_interval == 0 else ("IV" if chord_interval == 5 else "V")
            print(f"Bar {current_bar + 1}/12 - Playing {chord_name} chord")

            # 2. Play 4 beats for the current bar
            for beat in range(4):
                if not self.is_playing:
                    break
                    
                # -- DRUMS --
                # Ride cymbal on every beat
                self.fs.noteon(self.DRUM_CH, ride, 70) 
                
                # Kick on beats 1 and 3 (index 0 and 2)
                if beat in [0, 2]:
                    self.fs.noteon(self.DRUM_CH, kick, 100)
                
                # Snare on beats 2 and 4 (index 1 and 3)
                if beat in [1, 3]:
                    self.fs.noteon(self.DRUM_CH, snare, 100)
                    
                # -- BASS --
                # Basic pumping quarter notes on the root of the current chord
                self.fs.noteon(self.BASS_CH, current_bass_note, 110)
                
                # Wait for one beat
                time.sleep(beat_duration)
                
                # Note off
                self.fs.noteoff(self.BASS_CH, current_bass_note)
                
            bar_count += 1

    def cleanup(self):
        self.stop()
        self.fs.delete()


# Standalone Test
if __name__ == "__main__":
    engine = JamEngine()
    
    try:
        # Start a blues in A at 100 BPM
        engine.play_blues('A', 100)
        
        # Let it run for 30 seconds to hear the chord changes
        print("Listening for 30 seconds... (Press Ctrl+C to stop early)")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\nStopping Jam...")
    finally:
        engine.cleanup()
        print("Cleaned up.")