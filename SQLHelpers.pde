String getTuneName(String id) {
  sql.query("SELECT title FROM tune WHERE id=" + id);
  
  if (sql.next()) {
    return sql.getString(1);
  }
  
  return null;
}
