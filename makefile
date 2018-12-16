.PHONY: all run

OUT=exec/testing.wasm

all: $(OUT)

$(OUT): compiler/compiler.py
	compiler/compiler.py ../$@

run: all
	cd exec && node node_run.js
