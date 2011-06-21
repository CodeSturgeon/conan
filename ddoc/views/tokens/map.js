function(doc) {
  if(doc.doc_type == 'download') {
    for (var tok in doc.tokens) {
      emit(tok, doc.tokens[tok]);
    }
  }
}
