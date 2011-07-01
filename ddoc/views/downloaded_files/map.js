function(doc) {
  if (doc.doc_type === 'distribution') {
    for (var addr in doc.addresses) {
      var addr_data = doc.addresses[addr]
      var sent = false;
      for (var token in addr_data.tokens) {
        if (addr_data.tokens[token].use_time) {
          sent = true;
        }
      }
      if (sent) {
        for (var file in addr_data.files) {
          emit(addr_data.files[file], [addr, addr_data.name]);
        }
      }
    }
  }
}
