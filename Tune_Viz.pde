import de.bezier.data.sql.*;
import java.util.Collections;

PFont title_font;
PFont label_font;
PFont music_symbols;

PostgreSQL pgsql;

float[] p_keysigs = new float[12];
ArrayList[] p_key = new ArrayList[12];

final String TOTAL_SQL = "SELECT COUNT(id) from tune_viz_tune WHERE rhythm='jig'";

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
final float HSB_B = 0.7;

void setup() {
  size(600, 600);
  
  title_font = loadFont("GoudyStd-Bold-48.vlw");
  label_font = loadFont("GoudyStd-18.vlw");
  music_symbols = loadFont("Maestro-48.vlw");

  pgsql = new PostgreSQL(this, "localhost", "tunes", "esheehan", "");
  if (pgsql.connect()) {
    float total = 0.0;
    int total_keys = 0;
    
    // Initilialize the array of key signature probabilities
    for (int i = 0; i < p_keysigs.length; i++) {
      p_keysigs[i] = 0.0;
    }
    
    // Find the total number of jigs for probability calculations
    pgsql.query(TOTAL_SQL);
    if (pgsql.next()) {
      total = pgsql.getFloat(1);
    }
    
    pgsql.query(FREQ_PER_SHARPS_SQL);
    while (pgsql.next()) {
      p_keysigs[pgsql.getInt(1)] = pgsql.getFloat(2);
    }
    
    pgsql.query(FREQ_PER_FLATS_SQL);
    while (pgsql.next()) {
      p_keysigs[12 - pgsql.getInt(1)] = pgsql.getFloat(2);
    }

    for (int i = 0; i < p_keysigs.length; i++) {
      String sql = String.format(FREQ_PER_KEY_SQL, (i < 7) ? "s" : "f", (i < 7) ? i : 12 - i);
      pgsql.query(sql);
      
      ArrayList key_list = new ArrayList();
      while (pgsql.next()) {
        key_list.add(pgsql.getFloat(2) / p_keysigs[i]);
      }
      
      p_key[i] = key_list;
    }
    
    for (int i = 0; i < p_keysigs.length; i++) {
      p_keysigs[i] = p_keysigs[i] / total;
    }
      
  } else {
    println("Failed to connect to tunes database");
  }
  
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
  text("Key Distribution in Jigs", 0, -height/2 + 52);
  
  textFont(music_symbols);
  textAlign(LEFT);
  text("b", -width / 2 + 10, 24);
  textAlign(RIGHT);
  text("#", width / 2 - 10, 24);

  textFont(label_font);
  textAlign(CENTER);
  
  rotate(-PI/2);

  noStroke();
  pushMatrix();
  scale(SCALE_FACTOR);
  float theta = PI / 3;
  for (int i = 0; i < p_keysigs.length; i++) {
    drawStackedArc(p_key[i], p_keysigs[i], PI*pow(CENTER_R, 2)/12, theta);
    rotate(PI/6);
    theta = (theta + (PI / 6)) % (2*PI);
  }

  fill(0, 0, 1);
  ellipse(0, 0, CENTER_R * 2, CENTER_R * 2);
  popMatrix();

  // Magic number rotation!
  rotate(PI/2);
  
  int section = -1;
  if (mouseX == 0) {
    if (mouseY > 0) {
      section = 0;
    } else {
      section = 7;
    }
  } else {
    section = floor(atan(mouseY/mouseX) * 6 / PI);
  }
  
  for (int i = 0; i < p_keysigs.length; i++) {
    fill(0, 0, 0.6);

    text(str((i < 7) ? i : p_keysigs.length - i), 0, (-CENTER_R * SCALE_FACTOR) + 21);
    rotate(PI/6);
  }
}

void keyPressed() {
  switch (key) {
    case 's':
      saveFrame(str(year()) + str(month()) + str(day()) + str(hour()) + str(minute()) + str(second()) + "-jig-keys.png");
      break;
      
    default:
      break;
  }
}

void drawStackedArc(ArrayList data, float totalArea, float offset, float hsb_hue) {
  Collections.sort(data);
  float area = totalArea + offset;
  
  // Iterate from largest to smallest, drawing each arc
  for (int i = data.size() - 1; i >= 0; i--) {
    // Calculate the radius of this arc based on the remaining area.
    float r = sqrt(2 * area * (6 / PI));

    // DRAW!
    
    fill(hsb_hue, (data.size() - float(i)) / data.size(), HSB_B);
    arc(0, 0, r*2, r*2, -PI/12, PI/12);

    // Lastly, subtract the area of this segment from the drawing area.
    area -= ((Float) data.get(i)) * totalArea;
  }
}
