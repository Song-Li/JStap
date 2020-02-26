var cp = require("child_process");
function foo(c, d) {
  var b = c;
  b = d;
  console.log(b);
  cp.exec(b);
}
a = "abc";
foo(a, 123);
module.exports = {'foo': foo};
