function clone(obj) {
  var target = {};
  for (var i in obj) {
    target[i] = obj[i];
  }
  return target;
}

function(doc) {
  if(doc.doc_type == 'distribution') {
    for (var addr in doc.addresses) {
      for (var tok in doc.addresses[addr].tokens) {
        var token = clone(doc.addresses[addr].tokens[tok]);
        token.publication_id = doc.publication_id;
        token.files = doc.addresses[addr].files;

        emit(tok, token);
      }
    }
  }
}
