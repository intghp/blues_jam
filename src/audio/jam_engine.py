import time
import os
import platform
from PyQt6.QtCore import QThread, pyqtSignal

try:
    import fluidsynth
except ImportError:
    print("FluidSynth not found.")
    exit(1)

from src.core.music_theory import CHROMATIC_SCALE

class JamEngine(QThread):
    chord_changed = pyqtSignal(str)
    beat_tick = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.fs = fluidsynth.Synth()
        
        driver = 'dsound' if platform.system() == 'Windows' else 'coreaudio'
        try:
            self.fs.start(driver=driver)
        except:
            self.fs.start()
            
        sf2_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'FluidR3_GM.sf2')
        self.sfid = self.fs.sfload(sf2_path)
        
        self.BASS_CH = 0
        self.DRUM_CH = 9
        
        self.fs.program_select(self.BASS_CH, self.sfid, 0, 32)
        self.fs.program_select(self.DRUM_CH, self.sfid, 128, 0)
        
        self.is_playing = False
        
        self.current_root = 'A'
        self.bpm = 100

    def get_midi_root(self, note_name: str) -> int:
        base_c2_midi = 36
        note_index = CHROMATIC_SCALE.index(note_name.upper())
        return base_c2_midi + note_index

    def get_note_name_from_interval(self, root_note: str, interval: int) -> str:
        root_idx = CHROMATIC_SCALE.index(root_note.upper())
        target_idx = (root_idx + interval) % 12
        return CHROMATIC_SCALE[target_idx]

    def set_parameters(self, root_note: str, bpm: int):
        self.current_root = root_note
        self.bpm = bpm

    def run(self):
        self.is_playing = True
        beat_duration = 60.0 / self.bpm
        root_midi = self.get_midi_root(self.current_root)
        
        progression = [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7]
        
        kick = 36
        ride = 51
        snare = 38
        
        bar_count = 0
        
        while self.is_playing:
            current_bar = bar_count % 12
            chord_interval = progression[current_bar]
            current_bass_note = root_midi + chord_interval
            
            current_chord_name = self.get_note_name_from_interval(self.current_root, chord_interval)
            self.chord_changed.emit(current_chord_name)

            for beat in range(4):
                if not self.is_playing:
                    break
                    
                self.beat_tick.emit(beat)
                    
                self.fs.noteon(self.DRUM_CH, ride, 70) 
                
                if beat in [0, 2]:
                    self.fs.noteon(self.DRUM_CH, kick, 100)
                
                if beat in [1, 3]:
                    self.fs.noteon(self.DRUM_CH, snare, 100)
                    
                self.fs.noteon(self.BASS_CH, current_bass_note, 110)
                
                time.sleep(beat_duration)
                
                self.fs.noteoff(self.BASS_CH, current_bass_note)
                
            bar_count += 1

    def stop_jam(self):
        """Stops the thread safely."""
        self.is_playing = False
        self.wait()
        for i in range(128):
            self.fs.noteoff(self.BASS_CH, i)
            self.fs.noteoff(self.DRUM_CH, i)

    def cleanup(self):
        self.stop_jam()
        self.fs.delete()