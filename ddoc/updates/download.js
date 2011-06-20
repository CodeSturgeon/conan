function(doc, req) {
  var body = ""+JSON.stringify(doc,function(key,value){return value},2);
  return [doc, {body:body+"\n"}];
}
