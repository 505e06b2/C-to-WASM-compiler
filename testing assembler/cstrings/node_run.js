const fs = require("fs");
const typedArray = new Uint8Array(fs.readFileSync(process.argv[2]));

WebAssembly.instantiate(typedArray).then(result => {
	var ptr = result.instance.exports.get_str();
	const stack = new Uint8Array(result.instance.exports.memory.buffer);
	var string = "";
	for(; stack[ptr]; ptr++) {
		string += String.fromCharCode(stack[ptr]);
	}
	console.log(string);
});