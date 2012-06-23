function(doc) {
	if (doc.key && doc.rhythm) {
		emit([doc.key.count, doc.rhythm], 1);
	}
}