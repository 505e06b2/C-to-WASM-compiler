(module
	(import "imports" "puts" (func $_puts (param i32)))
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0x10000)) ;;end of memory: 65536kb

	(func $stack_alloc (param $size i32) (result i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.sub)
		(set_global $stacktop)
		(get_global $stacktop)
	)

	(func $stack_free (param $size i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.add)
		(set_global $stacktop)
	)

	(func $push (param $var i32)
		(i32.const 4)
		(call $stack_alloc)
		(get_local $var)
		(i32.store)
	)

	(func $pop
		(i32.const 4)
		(call $stack_free)
	)

	(func $_main (result i32)
		(local $stack i32) (i32.const 12) (call $stack_alloc) (set_local $stack)
		(i32.const 0) (get_local $stack) (i32.add);; Get z's pointer
		(i32.const 60);; putting z into wasm stack
		(i32.store);; storing z on the stack
		(i32.const 4) (get_local $stack) (i32.add);; Get x's pointer
		(i32.const 100);; putting x into wasm stack
		(i32.store);; storing x on the stack
		(i32.const 8) (get_local $stack) (i32.add);; Get y's pointer
		(i32.const 200);; putting y into wasm stack
		(i32.store);; storing y on the stack
		(i32.const 4) (get_local $stack) (i32.add);; Get x's pointer
 		(i32.load) (i32.const 8) (get_local $stack) (i32.add);; Get y's pointer
 		(i32.load) (i32.add) (i32.const 0) (get_local $stack) (i32.add);; Get z's pointer
 		(i32.load) (i32.add)
	)

	(export "main" (func $_main))
)
