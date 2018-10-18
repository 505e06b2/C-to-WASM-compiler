const fs = require("fs");
const typedArray = new Uint8Array(fs.readFileSync("main.wasm"));

const m = new WebAssembly.Memory({initial: 1});
const memory8 = new Uint8Array(m.buffer);

WebAssembly.instantiate(typedArray, {imports: {
		memory: m,
		puts: function(ptr) {
			var string = "";
			for(; memory8[ptr]; ptr++) {
				string += String.fromCharCode(memory8[ptr]);			
			}
			console.log(string);
		}
	}
});