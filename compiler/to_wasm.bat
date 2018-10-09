@echo off
set PATH=%CD%\..\bin;%PATH%
wat2wasm "%~1" -o "%~2"