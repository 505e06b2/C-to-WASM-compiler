@echo off
call "@compile.bat" "%~1"
node node_run.js "%~n1.wasm"