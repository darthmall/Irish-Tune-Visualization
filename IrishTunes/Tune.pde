class Tune {
  String title;
  ArrayList<Note> notes;
  
  Tune(String[] notes) {
    this.notes = new ArrayList<Note>();
    
    for (int i = 0; i < notes.length; i++) {
      String[] note = split(notes[i], "|");
      this.notes.add(new Note(float(note[0]), float(note[1])));
    }
  }

  void draw() {
    float offset = 0.0;

    beginShape();
    for (int i = 0; i < notes.size(); i++) {
      Note n = notes.get(i);

      if (n.pitchSpace > 0) {
        rect(offset, n.pitchSpace + noteHeight / 2.0, n.duration, noteHeight);
      }

      offset = offset + n.duration;
    }
    
    endShape();
  }
  
  float getWidth() {
    float w = 0.0;

    for (int i = 0; i < notes.size(); i++) {
      w = w + notes.get(i).duration;
    }

    return w;
  }
  
  float getRange() {
    float minPitch = -1.0;
    float maxPitch = 0.0;
    
    for (int i = 0; i < notes.size(); i++) {
      Note n = notes.get(i);
      if (n.pitchSpace > maxPitch) {
        maxPitch = n.pitchSpace;
      }
      
      if (n.pitchSpace < minPitch || minPitch < 0.0) {
        minPitch = n.pitchSpace;
      }
    }
    
    return (maxPitch - minPitch);
  }
}
