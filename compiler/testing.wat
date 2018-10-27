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

	(func $_ptr (param $g i32) (result i32)
		(local $stack i32) (i32.const 4) (call $stack_alloc) (set_local $stack)
		(i32.const 0) (get_local $stack) (i32.add) (get_local $g) (i32.store);; storing parameter on the stack
		(i32.const 0) (get_local $stack) (i32.add) (i32.load) (i32.const 222) (i32.store)
		(i32.const 999)
	)

	(func $_main (result i32)
		(local $stack i32) (i32.const 16) (call $stack_alloc) (set_local $stack)
		(i32.const 0) (get_local $stack) (i32.add) (i32.const 60) (i32.store);; storing z on the stack
		(i32.const 4) (get_local $stack) (i32.add) (i32.const 100) (i32.store);; storing x on the stack
		(i32.const 8) (get_local $stack) (i32.add) (i32.const 200) (i32.store);; storing y on the stack
		(i32.const 12) (get_local $stack) (i32.add) (i32.const 4) (get_local $stack) (i32.add) (call $_ptr) (i32.store);; storing a on the stack
		(i32.const 4) (get_local $stack) (i32.add) (i32.load) (i32.const 8) (get_local $stack) (i32.add) (i32.load) (i32.add) (i32.const 0) (get_local $stack) (i32.add) (i32.load) (i32.add)
	)

	(export "main" (func $_main))
)
