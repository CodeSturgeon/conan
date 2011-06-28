function(doc) {
  if (doc.doc_type == 'publication') {
    for (var fn in doc._attachments) {
      var digest = doc._attachments[fn]['digest'];
      emit([doc._id, fn], digest);
    }
  }
}
