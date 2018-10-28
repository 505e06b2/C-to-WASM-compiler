const fs = require("fs");
var typedArray = new Uint8Array(fs.readFileSync("testing.wasm"));

const memory = {};
const memoryDisplay = {
	char: {
		sizeof: 1,
		heading: "           00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f\n           -----------------------------------------------\n"
	},
	int: {
		sizeof: 4,
		heading: "              00       04       08       0c\n           -----------------------------------\n"
	}
}

function formattedMemoryDump(type, bytes = 256) {
	var str = memoryDisplay[type].heading;
	var offset = ((memory[type].length * memoryDisplay[type].sizeof) //to bytes
	             - bytes) / memoryDisplay[type].sizeof; //back to proper size
	var displayoffset = memory[type].length * memoryDisplay[type].sizeof - bytes;
	for(var y = 0; y < bytes / 16; y++) {
		str += (displayoffset).toString(16).padStart(8, "0") + " | ";
		for(var x = 0, xe = 16 / memoryDisplay[type].sizeof; x < xe; x++, offset++) {
			str += memory[type][offset].toString(16).padStart(memoryDisplay[type].sizeof*2, "0") + " ";
		}
		str += "\n";
		displayoffset += 16;
	}
	return str;
}

const memorytype = "int";
var dumpindex = 0;
WebAssembly.instantiate(typedArray, {
	debug: {
		viewmemory: function() {
			console.log(formattedMemoryDump(memorytype));
		},
		dumpmemory: function() {
			fs.writeFileSync("memory" + dumpindex + ".txt", formattedMemoryDump(memorytype, memory[memorytype].length * memoryDisplay[memorytype].sizeof));
			console.log(">>> Written memory to \"memory" + dumpindex + ".txt\"");
			dumpindex++;
		}
	},
	stdio: {
		puts: function(ptr) {
			var string = "";
			for(; memory.char[ptr]; ptr++) {
				string += String.fromCharCode(memory.char[ptr]);			
			}
			console.log(string);
		}
	}
}).then(result => {
	memory.char = new Uint8Array(result.instance.exports.memory.buffer);
	memory.int = new Uint32Array(result.instance.exports.memory.buffer);
	const main = result.instance.exports.main();
	console.log("Returned " + main);
});