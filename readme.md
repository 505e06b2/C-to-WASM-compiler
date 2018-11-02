# wasmcc - A C to WASM bytecode compiler

## What will the end product look like?
It will be a self contained .js file that will contain the entire WASM bytecode and any functions required for my compiler. It will also output .js files that do the same thing. It will be able to compile a subset of C99, but with limited optimizations, as this is my first compiler. A lot of people have trouble with understanding how memory works in their programs, and this project will hopefully be useful for showing, at least somewhat, what happens inside the machine at runtime.

## Goals:

Get Python feature-complete compiler finished <=== Current Target
* [ ] type checks at compile time
* * [x] int
* * [x] char
* * [x] short
* * [ ] unsigned types
* [ ] if statements
* [ ] loops
* * [ ] for
* * [ ] while
* [ ] scopes
* * [x] functions
* * [ ] if
* * [ ] blocks (manual)
* * [ ] loops
* [x] functions with params/returns
* [ ] pointers
* * [x] variables
* * [ ] functions
* [x] string literals
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