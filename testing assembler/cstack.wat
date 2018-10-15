(module
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0xFFFC)) ;;for alignment, we don't use the "first" 3 bytes
	
	(func $alloca (param $size i32) (result i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.sub)
		(set_global $stacktop)
		(get_global $stacktop)
	)
	
	(func $freea (param $size i32)
		(get_global $stacktop)
		(get_local $size)
		(i32.add)
		(set_global $stacktop)
	)
	
	(func $main (result i32)
		(i32.const 4)
		(call $alloca)
		(i32.const 300)
		(i32.store)
		
		(i32.const 4)
		(call $alloca)
		(i32.const 200)
		(i32.store)
		
		(i32.const 4)
		(call $alloca)
		(i32.const 100)
		(i32.store)
		
		(i32.const 4)
		(call $freea) ;;free 100
		
		(i32.const 4)
		(call $freea) ;;free 200
		
		(i32.const 4)
		(call $alloca) ;;we could have just remove that last freea and this alloca, but I wanted to test
		(i32.const 222)
		(i32.store)
		
		(i32.const 4)
		(get_global $stacktop)
		(i32.add) ;;Move pointer back to 300, it hasn't been overwritten, so alloca should still work
		(i32.const 333)
		(i32.store)
		
		(get_global $stacktop)
	)
	(export "main" (func $main))
)