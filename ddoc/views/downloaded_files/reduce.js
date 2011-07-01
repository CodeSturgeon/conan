function (key, values, rereduce) {
  var addrs = {};
  for (var vn in values) {
    addrs[values[vn][0]] = values[vn][1];
  }
  var returns = [];
  for (var addr in addrs) {
    returns.push([addr, addrs[addr]]);
  }
  return returns;
}
