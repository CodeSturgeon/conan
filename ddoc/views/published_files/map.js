function(doc) {
  if (doc.doc_type == 'publication') {
    for (var file in doc._attachments) {
      emit(file, null);
    }
  }
}
