import javax.sound.midi.*;

import de.bezier.data.sql.*;

HashMap<String, Tune> tunes;
ArrayList<String> tuneList;
ArrayList<String> selected;
int overIndex;

SQLite sql;

Sequencer sequencer;
long playbackPos = 0;
String currentlyPlaying;
boolean paused = false;

PFont univers;

float noteHeight = 10.0;

void setup() {
  size(1024, 768);
  BufferedReader reader = createReader("jigs.notes.csv");
  String l;

  tunes = new HashMap<String, Tune>();
  tuneList = new ArrayList<String>();
  selected = new ArrayList<String>();

  try {
    sequencer = MidiSystem.getSequencer();
    sequencer.open();
  } catch (Exception e) {}
  
  univers = loadFont("UniversLTStd-Cn-32.vlw");

  sql = new SQLite(this, "tunes.db");

  if (sql.connect()) {
    // Read in all the note data from the CSV for rendering the tunes on screen
    try {
      l = reader.readLine();
      
      while (l != null) {
        String[] data = split(l, ",");
        String name = getTuneName(data[0]);
        tunes.put(data[0], new Tune(name, subset(data, 1)));
        l = reader.readLine();
      }
    } catch (IOException e) {
      e.printStackTrace();
      noLoop();
    }
    
    // Populate the list of tunes.
    updateTuneSelection(null);
  } else {
    println("Failed to connect to PostgreSQL.");
    noLoop();
  }

  smooth();
}

void draw() {
  background(255);

  // FIXME: Debuggative line to make sure we're drawing things in the right place
  stroke(0);
  line(0, height * (4.0 / 5.0), width, height * (4.0 / 5.0));

  pushMatrix();
  translate(0, height * 0.9);

  overIndex = (mouseY > height * (4.0 / 5.0)) ? int(floor(mouseX / (width / tuneList.size()))) : -1;

  for (int i = 0; i < tuneList.size(); i++) {
    Tune t = tunes.get(tuneList.get(i));

    pushMatrix();
    scale(1.0 / tuneList.size());

    noStroke();
    if (i == overIndex) {
      fill(106, 116, 125, 64);
    } else {
      fill(106, 116, 125);
    }
    t.draw();

    popMatrix();

    translate(width / tuneList.size(), 0);
  }

  popMatrix();
  
  // Iterate over all selected tunes and draw them.
  pushMatrix();
  translate(20, height * 0.4);
  
  for (int i = selected.size() - 1; i >= 0; i--) {
    String tuneId = selected.get(i);

    noStroke();
    
    if (i % 2 == 0) {
      fill(234, 127, 30, 64);
    } else {
      fill(86, 162, 214);
    }

    tunes.get(selected.get(i)).draw();

    if (tuneId.equals(currentlyPlaying)) {
      break;
    }
  }

  if (tunes.size() > 0 && tuneList.size() > 0 && overIndex > -1) {
    fill(106, 116, 125, 64);
    tunes.get(tuneList.get(overIndex)).draw();
  }

  popMatrix();

  if (overIndex > -1) {
    fill(106, 116, 125);
    textFont(univers);
    textAlign(CENTER, CENTER);
    text(tunes.get(tuneList.get(overIndex)).name, width/2, height/2);
  }

  // Manually handle looping the sequence. If we've reached the end and
  // a new sequence has been selected, start that new sequence. Otherwise
  // loop the current one.
  if (!paused && !sequencer.isRunning() && selected.size() > 0) {
    String id = selected.get(selected.size() - 1);

    if (id.equals(currentlyPlaying)) {
      sequencer.setTickPosition(0);
      sequencer.start();
    } else {
      loadMidi(selected.get(selected.size() - 1));
    }
  }
  
  if (sequencer.isRunning()) {  
    playbackPos = sequencer.getTickPosition();
  }
}

void mouseClicked() {
  if (overIndex >= 0) {
    String id = tuneList.get(overIndex);
    selected.add(id);
    updateTuneSelection(id);
  }
}

void keyPressed() {
  if (key == ' ') {
    if (sequencer.isRunning()) {
      paused = true;
      sequencer.stop();
    } else {
      paused = false;
      sequencer.setTickPosition(playbackPos);
      sequencer.start();
    }
  }
}

void loadMidi(String id) {
  try {
    File midiFile = new File(dataPath("midi/" + id + ".mid"));
    Sequence sequence = MidiSystem.getSequence(midiFile);
    sequencer.setSequence(sequence);
    currentlyPlaying = id;

    sequencer.start();
  } catch (Exception e) {}
}

void updateTuneSelection(String id) {
  if (id == null) {
    sql.query("SELECT * FROM similar_tunes LIMIT 10");
  } else {
    sql.query("SELECT * FROM similar_tunes WHERE id=" + id + " OR target_id=" + id + " LIMIT 10");
  }
  
  tuneList.clear();
  
  while (sql.next() && tuneList.size() < 5) {
    String tuneId = sql.getString(1);
    
    if (!tuneId.equals(id) && !tuneList.contains(tuneId) && !selected.contains(tuneId)) {
      tuneList.add(tuneId);
    }
    
    tuneId = sql.getString(3);
    if (!tuneId.equals(id) && !tuneList.contains(tuneId) && !selected.contains(tuneId)) {
      tuneList.add(tuneId);
    }
  }
}
