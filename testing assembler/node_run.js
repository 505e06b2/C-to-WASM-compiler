const fs = require("fs");
const typedArray = new Uint8Array(fs.readFileSync(process.argv[2]));

WebAssembly.instantiate(typedArray).then(result => {
	console.log("main returned: " + result.instance.exports.main());
});