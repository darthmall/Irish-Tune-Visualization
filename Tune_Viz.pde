import de.bezier.data.sql.*;

PFont title_font;
PFont label_font;

PostgreSQL pgsql;

HashMap<Integer, Float> sharps = new HashMap<Integer, Float>();
HashMap<Integer, Float> flats = new HashMap<Integer, Float>();

final String TOTAL_SQL = "SELECT COUNT(id) from tune_viz_tune WHERE rhythm='jig'";
final String SHARPS_SQL = "SELECT key.number_of_accidentals, count(tune.id)" +
                          " FROM tune_viz_tune AS tune" +
                          " JOIN tune_viz_key AS key ON (tune.key_id = key.id)" +
                          " WHERE tune.rhythm='jig' AND key.accidentals='s'" +
                          " GROUP BY key.number_of_accidentals";
final String FLATS_SQL = "SELECT key.number_of_accidentals, count(tune.id)" +
                         " FROM tune_viz_tune AS tune" +
                         " JOIN tune_viz_key AS key ON (tune.key_id = key.id)" +
                         " WHERE tune.rhythm='jig' AND key.accidentals='f'" +
                         " GROUP BY key.number_of_accidentals";

final int R = 300;


void setup() {
  size(600, 600);
  
  title_font = loadFont("GoudyStd-Bold-48.vlw");
  label_font = loadFont("GoudyStd-18.vlw");

  pgsql = new PostgreSQL(this, "localhost", "tunes", "esheehan", "");
  if (pgsql.connect()) {
    float total = 0.0;
    int total_keys = 0;
    
    // Find the total number of jigs for probability calculations
    pgsql.query(TOTAL_SQL);
    if (pgsql.next()) {
      total = pgsql.getFloat(1);
    }
    
    
    // Find all the keys according to how many sharps they have
    pgsql.query(SHARPS_SQL);
    while (pgsql.next()) {
      total_keys++;
      sharps.put(pgsql.getInt(1), pgsql.getFloat(2) / total);
    }
    
    pgsql.query(FLATS_SQL);
    while (pgsql.next()) {
      total_keys++;
      flats.put(pgsql.getInt(1), pgsql.getFloat(2) / total);
    }
  } else {
    println("Failed to connect to tunes database");
  }
  
  colorMode(HSB, 360, 100, 100);
}

void draw() {
  background(0, 0, 100);

  int i = 0;
  float theta = 0;
  translate(width / 2, height / 2);

  textFont(title_font);
  fill(8, 50, 82);
  textAlign(CENTER);
  text("Key Distribution in Jigs", 0, -height/2 + 52);
  
  textFont(label_font);
  
  Iterator iter = sharps.entrySet().iterator();
  while (iter.hasNext()) {
    Map.Entry entry = (Map.Entry) iter.next();
    float a = ((Float) entry.getValue()) * TWO_PI;
    
    fill(124, 19, calcSats((Integer) entry.getKey()));
    noStroke();
    smooth();
    arc(0, 0, R, R, theta, theta + a);
    
    float text_angle = theta + (a/2);
    if (text_angle > PI / 2 && text_angle < 0.75 * TWO_PI) {
      textAlign(RIGHT);
    } else {
      textAlign(LEFT);
    }

    text(entry.getKey() + " sharps", (R/2 + 10) * cos(text_angle), (R/2 + 10) * sin(text_angle));
    noSmooth();

    theta += a;
    i++;
  }
  
  iter = flats.entrySet().iterator();
  while (iter.hasNext()) {
    Map.Entry entry = (Map.Entry) iter.next();
    float a = ((Float) entry.getValue()) * TWO_PI;
    
    fill(338, 45, calcSats((Integer) entry.getKey()));
    noStroke();
    smooth();
    arc(0, 0, R, R, theta, theta + a);
    
    float text_angle = theta + (a/2);
    if (text_angle > PI / 2 && text_angle < 0.75 * TWO_PI) {
      textAlign(RIGHT);
    } else {
      textAlign(LEFT);
    }

    text(entry.getKey() + " flats", (R/2 + 10) * cos(text_angle), (R/2 + 10) * sin(text_angle));
    noSmooth();

    theta += a;
    i++;
  }
}

int calcSats(Integer accidentals) {
  return 20 + (80 * accidentals / 7);
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
