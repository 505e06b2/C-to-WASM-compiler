(module
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0xFFFC)) ;;for alignment, we don't use the "first" 3 bytes
	(global $scope (mut i32) (i32.const 0))
	
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
	
	(func $main (result i32)
		(i32.const 4)
		(call $stack_alloc)
		(i32.const 300)
		(i32.store)
		
		(i32.const 4)
		(call $stack_alloc)
		(i32.const 200)
		(i32.store)
		
		(i32.const 4)
		(call $stack_alloc)
		(i32.const 100)
		(i32.store)
		
		(i32.const 4)
		(call $stack_free) ;;free 100
		
		(i32.const 4)
		(call $stack_free) ;;free 200
		
		(i32.const 4)
		(call $stack_alloc) ;;we could have just remove that last stack_free and this stack_alloc, but I wanted to test
		(i32.const 222)
		(i32.store)
		
		(i32.const 4)
		(get_global $stacktop)
		(i32.add) ;;Move pointer back to 300, it hasn't been overwritten, so stack_alloc should still work
		(i32.const 333)
		(i32.store)
		
		(get_global $stacktop)
	)
	(export "main" (func $main))
)