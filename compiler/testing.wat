(module
	(import "imports" "puts" (func $_puts (param i32)))
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0x10000)) ;;end of memory: 65536kb

	(func $stack_alloc (param $size i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.sub)
		(set_global $stacktop)
	)

	(func $stack_free (param $size i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.add)
		(set_global $stacktop)
	)

	(func $_ptr (param $a i32) (param $b i32) (result i32)
		(i32.const 8) (call $stack_alloc);; allocate space on the stack
		(i32.const 0) (get_global $stacktop) (i32.add) (get_local $a) (i32.store);; storing parameter on the stack
		(i32.const 4) (get_global $stacktop) (i32.add) (get_local $b) (i32.store);; storing parameter on the stack
		(i32.const 0) (get_global $stacktop) (i32.add) (i32.load) (i32.const 4) (get_global $stacktop) (i32.add) (i32.load) (i32.load) (i32.store);; assigning to pointer location
		(i32.const 0xAABBCCDD);; Return
		(i32.const 8) (call $stack_free);; free stack reserved previously
	)

	(func $_main (result i32)
		(i32.const 16) (call $stack_alloc);; allocate space on the stack
		(i32.const 0) (get_global $stacktop) (i32.add) (i32.const 0xDEADBEEF) (i32.store);; storing z on the stack
		(i32.const 4) (get_global $stacktop) (i32.add) (i32.const 0x12345678) (i32.store);; storing x on the stack
		(i32.const 8) (get_global $stacktop) (i32.add) (i32.const 0xDEADBEEF) (i32.store);; storing y on the stack
		(i32.const 12) (get_global $stacktop) (i32.add) (i32.const 8) (get_global $stacktop) (i32.add) (i32.const 4) (get_global $stacktop) (i32.add) (call $_ptr) (i32.store);; storing w on the stack
		(i32.const 12) (get_global $stacktop) (i32.add) (i32.const 0) (get_global $stacktop) (i32.add) (i32.const 4) (get_global $stacktop) (i32.add) (call $_ptr) (i32.store)
		(i32.const 0x00000000);; Return
		(i32.const 16) (call $stack_free);; free stack reserved previously
	)

	(export "main" (func $_main))
)
