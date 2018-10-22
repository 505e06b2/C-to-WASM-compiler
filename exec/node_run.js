const fs = require("fs");
var typedArray = new Uint8Array(fs.readFileSync("testing.wasm"));

var memory8;
WebAssembly.instantiate(typedArray, {imports: {
		puts: function(ptr) {
			var string = "";
			for(; memory8[ptr]; ptr++) {
				string += String.fromCharCode(memory8[ptr]);			
			}
			console.log(string);
		}
	}
}).then(result => {
	memory8 = new Uint8Array(result.instance.exports.memory.buffer);
	memory32 = new Uint32Array(result.instance.exports.memory.buffer);
	const main = result.instance.exports.main();
	console.log("" + memory32);
	console.log("Returned " + main);
});