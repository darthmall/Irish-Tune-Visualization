import javax.sound.midi.*;

import de.bezier.data.sql.*;

import controlP5.*;

HashMap<String, Tune> tunes;
ArrayList<String> tuneList;
ArrayList<String> selected;
int overIndex;

ControlP5 controlP5;
ControlWindow controlWindow;

SQLite sql;

Sequencer sequencer;

PFont univers;

float scaleX = 16.77;
float scaleY = 4.6;
float noteHeight = 1.0;

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

    // Set up the controls for selecting the next tune.
    controlP5 = new ControlP5(this);
    controlWindow = controlP5.addControlWindow("Window Controls", 100, 100, 400, 200)
        .hideCoordinates()
        .setBackground(color(40));
    
    controlP5.addSlider("scaleX")
        .setRange(1, 20)
        .setPosition(40, 40)
        .setSize(200, 29)
        .setValue(scaleX)
        .setWindow(controlWindow);
    controlP5.addSlider("scaleY")
        .setRange(1, 20)
        .setPosition(40, 79)
        .setSize(200, 29)
        .setValue(scaleY)
        .setWindow(controlWindow);
    controlP5.addSlider("noteHeight")
        .setRange(1, 10)
        .setPosition(40, 118)
        .setSize(200, 29)
        .setValue(noteHeight)
        .setWindow(controlWindow);
    
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

  pushMatrix();
  translate(0, height * 0.5);
  
  overIndex = (mouseY > height / 2) ? int(floor(mouseX / (width / tuneList.size()))) : -1;

  for (int i = 0; i < tuneList.size(); i++) {
    Tune t = tunes.get(tuneList.get(i));

    pushMatrix();
    scale((width / tuneList.size()) / t.getWidth());

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
  translate(20, 0);
  scale(scaleX, scaleY);
  
  for (int i = 0; i < selected.size(); i++) {


    noStroke();
    
    if (i % 2 == 0) {
      fill(234, 127, 30, 64);
    } else {
      fill(86, 162, 214);
    }

    tunes.get(selected.get(i)).draw();
  }
  
  popMatrix();

  if (overIndex > -1) {
    fill(106, 116, 125);
    textFont(univers);
    textAlign(CENTER, CENTER);
    text(tunes.get(tuneList.get(overIndex)).name, width/2, height/2);
  }
}

void controlEvent(ControlEvent ev) {
  String name = ev.getName();
  
  if (name.equals("scaleX")) {
    scaleX = ev.getValue();
  } else if (name.equals("scaleY")) {
    scaleY = ev.getValue();
  } else if (name.equals("noteHeight")) {
    noteHeight = ev.getValue();
  }
}

void mouseClicked() {
  if (overIndex >= 0) {
    String id = tuneList.get(overIndex);
    selected.add(id);
    updateTuneSelection(id);
    loadMidi(id);
  }
}

void keyPressed() {
  if (key == ' ') {
    if (sequencer.isRunning()) {
      sequencer.stop();
    } else {
      sequencer.start();
    }
  }
}

void loadMidi(String id) {
  try {
    File midiFile = new File(dataPath("midi/" + id + ".mid"));
    Sequence sequence = MidiSystem.getSequence(midiFile);
    sequencer.setSequence(sequence);

    // Set up infinite looping!
    sequencer.setLoopCount(Sequencer.LOOP_CONTINUOUSLY);
    sequencer.setLoopStartPoint(0);
    sequencer.setLoopEndPoint(-1);

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
