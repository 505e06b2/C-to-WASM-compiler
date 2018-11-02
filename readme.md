
# wasmcc - A C to WASM bytecode compiler

## Goals:

Get Python prototype transpiler complete <=== Current Target
* [ ] typing (other than int)
* [ ] if statements
* [ ] for/while loops
* [ ] block scopes (only functions have their own scope atm)
* [x] functions with params/returns
* [x] pointers
* [ ] Inline JS (for importing functions)
* [ ] Inline WASM (for optimisation)

Get C bytecode assembler working to replace wabt (wabt currently uses C++)
>this will use the same S-expression format as wabt

Alter prototype to use/test this assembler

Get C99 lexer/parser working to feed the assembler

Work on some sort of GCC-style preprocessor
* [ ] C/C++ style comments
* [ ] Includes (not sure how this will work platform agnostically)
* [ ] Ifdefs/defines/etc
* [ ] Macros (low priority)

Done?