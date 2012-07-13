import de.bezier.data.sql.*;
import java.util.Collections;

PFont title_font;
PFont label_font;
PFont music_symbols;
PFont console_font;

PostgreSQL pgsql;

float total_tunes;
KeySig[] keySignatures = new KeySig[12];

final String TOTAL_SQL = "SELECT COUNT(id) from tune_viz_tune WHERE rhythm='jig'";
final String BUCKET_SQL = "select tune.id, key.accidentals, key.number_of_accidentals, pc.pitch, pc.count" +
                          " from tune_viz_tune as tune" +
                          " join tune_viz_key as key on (tune.key_id = key.id)" +
                          " join tune_viz_pitchclass as pc on (pc.tune_id = tune.id)" +
                          " where tune.rhythm='jig'" +
                          " group by key.accidentals, key.number_of_accidentals, key.degree, key.name, tune.id, pc.pitch, pc.count" +
                          " order by key.accidentals desc, key.number_of_accidentals, key.degree, tune.id";

final int SCALE_FACTOR = 150;
final float CENTER_R = 0.4;
final float HSB_B = 0.93;

void setup() {
  size(600, 600);
  
  title_font = loadFont("GoudyStd-Bold-48.vlw");
  label_font = loadFont("GoudyStd-18.vlw");
  music_symbols = loadFont("Maestro-48.vlw");
  console_font = loadFont("Anonymous-18.vlw");

  pgsql = new PostgreSQL(this, "localhost", "tunes", "esheehan", "");
  if (pgsql.connect()) {
    pgsql.query(TOTAL_SQL);
    if (pgsql.next()) {
      total_tunes = pgsql.getFloat(1);
    }
    
    pgsql.query(BUCKET_SQL);
    while (pgsql.next()) {
      int id = pgsql.getInt(1);
      String accidentals = pgsql.getString(2);
      int accidentalCount = pgsql.getInt(3);
      String pitchName = pgsql.getString(4);
      float pitchCount = pgsql.getFloat(5);
      int signatureIdx = (accidentals.equals("s")) ? accidentalCount : 12 - accidentalCount;
      
      if (keySignatures[signatureIdx] == null) {
        keySignatures[signatureIdx] = new KeySig();
      }
      
      Tune t = keySignatures[signatureIdx].getTune(id);
      t.buckets.put(pitchName, pitchCount);
    }
    
    colorMode(HSB, 2*PI, 1, 1);
    smooth();
  } else {
    println("Failed to connect to tunes database");
  }
}

void draw() {
  background(0, 0, 1);
  
  // Position the origin for ease of calculations. Huzzah for affine transformations!
  translate(width / 2, height / 2);

  textFont(title_font);
  fill(0, 1, 0);
  textAlign(CENTER);
  text("Note Distributions of Jigs", 0, -height/2 + 52);
  
  textFont(music_symbols);
  textAlign(LEFT);
  text("b", -width / 2 + 10, 24);
  textAlign(RIGHT);
  text("#", width / 2 - 10, 24);

  textFont(label_font);
  textAlign(CENTER);
  
  rotate(-PI/2);

  int section = -1;
  float x = mouseX - (width / 2);
  float y = mouseY - (height / 2);
  float a = atan(y / x) + (PI/2) + (PI/12);
  if (x == 0) {
    if (mouseY > 0) {
      section = 0;
    } else {
      section = 7;
    }
  } else {
    section = floor(a * 6 / PI);
    
    if (x < 0) {
      section = 6 + section;
    }
    
    section = section % 12;
  }
  
  noStroke();
  pushMatrix();
  scale(SCALE_FACTOR);
  float hueAngle = PI/3;
  for (int i = 0; i < keySignatures.length; i++) {
    
    if (keySignatures[i] != null) {
      float theta = (PI/6) / keySignatures[i].tunes.size();
      Iterator it = keySignatures[i].tunes.entrySet().iterator();

      println(String.format("%d tunes ==> theta = %f radians", keySignatures[i].tunes.size(), theta));

      while (it.hasNext()) {
        Map.Entry pair = (Map.Entry) it.next();
        Tune tune = (Tune) pair.getValue();
        
        drawStackedArc(tune,
                       theta,
                       (1 / total_tunes),
                       theta * pow(CENTER_R,2),
                       hueAngle,
                       HSB_B * ((i == section) ? 1.33 : 1));
        rotate(theta);
      }         
    }

    hueAngle = (hueAngle + (PI/6)) % (2*PI);
  }

  fill(0, 0, 1);
  ellipse(0, 0, CENTER_R * 2, CENTER_R * 2);
  popMatrix();

  // Magic number rotation!
  rotate(PI/2);
  
  pushMatrix();
  for (int i = 0; i < keySignatures.length; i++) {
    if (i == section) {
      fill(((PI / 3) + (i * PI / 6)) % (2 * PI), 1.0, HSB_B);
    } else {
      fill(0, 0, 0.6);
    }

    text(str((i < 7) ? i : keySignatures.length - i), 0, (-CENTER_R * SCALE_FACTOR) + 21);
    rotate(PI/6);
  }
  popMatrix();
}

void drawStackedArc(Tune tune, float theta, float totalArea, float offset, float hsb_hue, float hsb_brightness) {
  float totalNotes = tune.totalNotes();
  float area = totalArea + offset;
  int i = 0;

  // Draw from the outside in...
  Iterator it = tune.buckets.entrySet().iterator();
  while (it.hasNext()) {
    Map.Entry pair = (Map.Entry) it.next();

    // Calculate the radius of this arc based on the remaining area.
    float r = sqrt(2 * area / theta);

    // DRAW!
    fill(hsb_hue, (totalNotes - i) * (0.8 / totalNotes) + 0.1, hsb_brightness);
    arc(0, 0, r*2, r*2, 0, theta);

    // Lastly, subtract the area of this segment from the drawing area.
    float p = ((Float) pair.getValue()) / totalNotes;
    area -= p * totalArea;
    
    println(String.format("%s ==> %f / %f = %f", (String) pair.getKey(), (Float) pair.getValue(), totalNotes, p));

    // Increment the counter we use to calculate saturation
    i++;
  }
}

class KeySig {
  protected HashMap<Integer, Tune> tunes;
  
  public KeySig() {
    tunes = new HashMap<Integer, Tune>();
  }
  
  public Tune getTune(Integer id) {
    if (!tunes.containsKey(id)) {
      tunes.put(id, new Tune());
    }
    
    return tunes.get(id);
  }
}

class Tune {
  protected HashMap<String, Float> buckets;
  
  public Tune() {
    buckets = new HashMap<String, Float>();
  }
  
  public float totalNotes() {
    float count = 0;
    Iterator it = buckets.entrySet().iterator();
    
    while (it.hasNext()) {
      Map.Entry pair = (Map.Entry) it.next();
      count = count + ((Float) pair.getValue());
    }
    
    return count;
  }
}
