# wasmcc - A C to WASM bytecode compiler

## Goals:
Get Python prototype transpiler complete
* int / uint types
* if statements
* for/while loops
* block scopes
* functions with params/returns
* pointers

Get C bytecode assembler working to replace wabt
>might use intermediate language, but this will most likely be S-Expressions

Alter prototype to use/test this assembler

Get C99 lexer/parser working to feed the assembler

Work on some sort of GCC-style preprocessor

Done?