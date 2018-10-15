const fs = require("fs");
const typedArray = new Uint8Array(fs.readFileSync(process.argv[2]));

WebAssembly.instantiate(typedArray).then(result => {
	const main = result.instance.exports.main();
	const stack = new Uint32Array(result.instance.exports.memory.buffer);
	console.log("Bottom of stack: " + stack)
	console.log("main returned: " + main);
});