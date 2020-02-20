var cp = require("child_process");
function foo() {
  var a = 123;
  var b = a;
  console.log(b);
  cp.exec(b);
}
module.exports = {foo: foo};
