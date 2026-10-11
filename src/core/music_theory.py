# The Western chromatic scale (using sharps by default to simplify initial logic)
CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale formulas in semitones (distance from the root note)
SCALE_FORMULAS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'minor_pentatonic': [0, 3, 5, 7, 10],
    'major_pentatonic': [0, 2, 4, 7, 9],
    'blues': [0, 3, 5, 6, 7, 10] # Adds the Blue Note (b5) to the minor pentatonic
}

class Fretboard:
    def __init__(self, tuning: list[str] = ['E', 'A', 'D', 'G', 'B', 'E'], frets: int = 20):
        """
        Initializes the acoustic guitar fretboard. 
        For acoustic guitars, 20 frets is standard.
        The default tuning is Standard (E A D G B E), read from the lowest string to the highest.
        """
        self.tuning = tuning
        self.frets = frets
        self.matrix = self._generate_fretboard()

    def _generate_fretboard(self) -> list[list[str]]:
        """
        Generates a 2D matrix where each row is a string and each column is a fret.
        matrix[0][0] = E (6th string open)
        matrix[0][1] = F (6th string, 1st fret)
        """
        fretboard = []
        for string_root in self.tuning:
            # Find the index of the open string note in the chromatic scale
            root_index = CHROMATIC_SCALE.index(string_root.upper())
            string_notes = []
            
            # Calculate the note for each fret
            for fret in range(self.frets + 1): # +1 to include the open string (fret 0)
                note_index = (root_index + fret) % 12
                string_notes.append(CHROMATIC_SCALE[note_index])
                
            fretboard.append(string_notes)
            
        return fretboard

    def get_scale_notes(self, root_note: str, scale_type: str) -> list[str]:
        """
        Returns the notes of a specific scale starting from a root note.
        Ex: get_scale_notes('A', 'minor_pentatonic') -> ['A', 'C', 'D', 'E', 'G']
        """
        if scale_type not in SCALE_FORMULAS:
            raise ValueError(f"Scale '{scale_type}' not found. Available options: {list(SCALE_FORMULAS.keys())}")

        root_index = CHROMATIC_SCALE.index(root_note.upper())
        formula = SCALE_FORMULAS[scale_type]
        
        scale_notes = []
        for interval in formula:
            note_index = (root_index + interval) % 12
            scale_notes.append(CHROMATIC_SCALE[note_index])
            
        return scale_notes

    def find_notes_on_fretboard(self, notes_to_find: list[str]) -> list[tuple[int, int, str]]:
        """
        Searches for specific notes across the entire fretboard.
        Returns a list of tuples: (string_index, fret_index, note)
        """
        positions = []
        for string_idx, string_notes in enumerate(self.matrix):
            for fret_idx, note in enumerate(string_notes):
                if note in notes_to_find:
                    positions.append((string_idx, fret_idx, note))
                    
        return positions


# Simple test block to validate if the logic is working.
# This will only be executed if you run this file directly.
if __name__ == "__main__":
    guitar = Fretboard()
    
    print("--- Logic Engine Test ---")
    
    # 1. Testing the A Minor Pentatonic
    a_minor_penta_notes = guitar.get_scale_notes('A', 'minor_pentatonic')
    print(f"A Minor Pentatonic notes: {a_minor_penta_notes}")
    
    # 2. Testing the E Blues Scale
    e_blues_notes = guitar.get_scale_notes('E', 'blues')
    print(f"E Blues Scale notes: {e_blues_notes}")
    
    # 3. Mapping the A Minor Pentatonic on the fretboard
    positions = guitar.find_notes_on_fretboard(a_minor_penta_notes)
    print("\nSome positions of the Am Pentatonic on the guitar (String, Fret, Note):")
    
    # Printing only the first 10 to avoid cluttering the terminal
    for pos in positions[:10]:
        print(f"String {pos[0]+1} (lowest) -> Fret {pos[1]}: {pos[2]}")