function(newDoc, oldDoc, userCtx) {
  var body = ""+JSON.stringify(oldDoc,function(key,value){return value},2);
  //throw({forbidden:body});
}
