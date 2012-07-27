import de.bezier.data.sql.*;
import java.util.Collections;

PFont title_font;
PFont label_font;
PFont music_symbols;
PFont console_font;

boolean debug = false;

PostgreSQL pgsql;

float total_tunes;
KeySig[] keySignatures = new KeySig[12];

final String TOTAL_SQL = "SELECT COUNT(id) from tune_viz_tune WHERE rhythm='jig'";

final String FREQUENCIES_SQL = "select key.name, key.number_of_accidentals, key.accidentals, key.degree, count(tune.id)" +
                   " from tune_viz_tune as tune" +
                   " join tune_viz_key as key on (key.id = tune.key_id)" +
                   " where tune.rhythm='jig'" +
                   " group by key.name, key.number_of_accidentals, key.accidentals, key.degree" +
                   " order by key.accidentals desc, key.number_of_accidentals, key.degree";

final String FREQ_PER_SHARPS_SQL = "SELECT key.number_of_accidentals, count(tune.id)" +
                          " FROM tune_viz_tune AS tune" +
                          " JOIN tune_viz_key AS key ON (tune.key_id = key.id)" +
                          " WHERE tune.rhythm='jig' AND key.accidentals='s'" +
                          " GROUP BY key.number_of_accidentals";

final String FREQ_PER_FLATS_SQL = "SELECT key.number_of_accidentals, count(tune.id)" +
                         " FROM tune_viz_tune AS tune" +
                         " JOIN tune_viz_key AS key ON (tune.key_id = key.id)" +
                         " WHERE tune.rhythm='jig' AND key.accidentals='f'" +
                         " GROUP BY key.number_of_accidentals" +
                         " ORDER BY key.number_of_accidentals DESC";
                         
final String FREQ_PER_KEY_SQL = "SELECT key.name, count(tune.id)" +
                                " FROM tune_viz_tune AS tune" +
                                " JOIN tune_viz_key as key ON (tune.key_id = key.id)" +
                                " WHERE tune.rhythm='jig' AND key.accidentals='%s' AND key.number_of_accidentals=%d" +
                                " GROUP BY key.name";

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
    
    // Find the total number of jigs for probability calculations
    pgsql.query(TOTAL_SQL);
    if (pgsql.next()) {
      total_tunes = pgsql.getFloat(1);
    }

    pgsql.query(FREQUENCIES_SQL);
    while(pgsql.next()) {
      String accidentals = pgsql.getString(3);
      int signatureIdx = (accidentals.equals("s")) ? pgsql.getInt(2) : 12 - pgsql.getInt(2);
      
      println(String.format("%s %d ==> %d", accidentals, pgsql.getInt(2), signatureIdx));

      if (keySignatures[signatureIdx] == null) {
        keySignatures[signatureIdx] = new KeySig();
      }
      
      keySignatures[signatureIdx].addKey(pgsql.getString(1), pgsql.getInt(4), pgsql.getInt(5));
    }
      
  } else {
    println("Failed to connect to tunes database");
  }
  
  // Set up HSB color space so that we can equate radians to hues and probabilities to saturation and brightness.
  colorMode(HSB, 2*PI, 1.0, 1.0);
  smooth();
}

void draw() {
  background(0, 0, 1);
  
  // Position the origin for ease of calculations. Huzzah for affine transformations!
  translate(width / 2, height / 2);

  textFont(title_font);
  fill(0, 1, 0);
  textAlign(CENTER);
  text("Key Signatures of Jigs", 0, -height/2 + 52);
  
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
  float theta = PI / 3;
  for (int i = 0; i < keySignatures.length; i++) {
    if (keySignatures[i] != null) {
      drawStackedArc(keySignatures[i],
                     PI*pow(CENTER_R, 2)/12,
                     theta,
                     HSB_B * ((i == section) ? 1.33 : 1));
    }

    rotate(PI/6);
    theta = (theta + (PI/6)) % (2*PI);
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
  
  if (debug) {
    textFont(console_font);
    fill(0, 0, 0.6);
    textAlign(LEFT);
    text(String.format("(%d, %d); %f rad; section: %d", int(x), int(y), a, section), -width/2, height/2 - 4);
  }
}

void keyPressed() {
  switch (key) {
    case 's':
      saveFrame(str(year()) + str(month()) + str(day()) + str(hour()) + str(minute()) + str(second()) + "-jig-keys.png");
      break;
      
    case TAB:
      debug = !debug;
      break;
      
    default:
      break;
  }
}

void drawStackedArc(KeySig sig, float offset, float hsb_hue, float hsb_brightness) {
  float totalArea = float(sig.total) / total_tunes;
  float area = totalArea + offset;

  // Draw from the outside in...
  for (int i = sig.keys.length - 1; i >= 0; i--) {
    if (sig.keys[i] != null) {
      // Calculate the radius of this arc based on the remaining area.
      float r = sqrt(2 * area * (6 / PI));
  
      // DRAW!
      fill(hsb_hue, (sig.keys.length - i) * (0.8 / sig.keys.length) + 0.1, hsb_brightness);
      arc(0, 0, r*2, r*2, -PI/12, PI/12);
  
      // Lastly, subtract the area of this segment from the drawing area.
      area -= (float(sig.keys[i].count) / float(sig.total)) * totalArea;
    }
  }
}

protected class KeySig {
  protected int total;
  protected KeyBucket[] keys;
  
  public KeySig() {
    keys = new KeyBucket[7];
  }
  
  public void addKey(String keyName, int scaleDegree, int count) {
    int index = scaleDegree - 1;

    if (keys[index] == null) {
      keys[index] = new KeyBucket(keyName);
    }
    
    keys[index].count = count;
    
    // Recalculate the total number of tunes in this key signature.
    total = 0;
    for (int i = 0; i < keys.length; i++) {
      if (keys[i] != null) {
        total += keys[i].count;
      }
    }
    
  }
  
}

protected class KeyBucket {
  protected String name;
  protected int count;
  
  public KeyBucket(String name) {
    this.name = name;
    this.count = 0;
  }

}
