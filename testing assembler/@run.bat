@echo off
set PATH=%~dp0\..\bin;%PATH%
cd "%~1"
wat2wasm main.wat
node node_run.js main.wasm
cd ..