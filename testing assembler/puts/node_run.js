const fs = require("fs");
const typedArray = new Uint8Array(fs.readFileSync("main.wasm"));

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
	result.instance.exports.main();
});