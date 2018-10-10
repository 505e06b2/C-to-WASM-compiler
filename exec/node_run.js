const fs = require("fs");
var typedArray = new Uint8Array(fs.readFileSync("testing.wasm"));
WebAssembly.instantiate(typedArray).then(result => {
	console.log("main returned: " + result.instance.exports.main());
});