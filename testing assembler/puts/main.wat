(module
	(import "imports" "memory" (memory 1))
	(import "imports" "puts" (func $_puts (param i32)))
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
	
	(func $_main
		(local $ptr i32)
		(local $start_ptr i32)
		(i32.const 8)
		(call $stack_alloc)
		
		(tee_local $start_ptr) ;;keep track of the start
		(tee_local $ptr) ;;ptr now points to first index
		(i32.const 65)
		(i32.store8)
		
		(get_local $ptr)
		(i32.const 1)
		(i32.add) ;;inc ptr
		
		(tee_local $ptr) ;;ptr now points to second index
		(i32.const 66)
		(i32.store8)
		
		(get_local $ptr)
		(i32.const 1)
		(i32.add) ;;inc ptr
		
		(tee_local $ptr) ;;ptr now points to third index
		(i32.const 67)
		(i32.store8)
		
		(get_local $ptr)
		(i32.const 1)
		(i32.add) ;;inc ptr
		
		(tee_local $ptr) ;;ptr now points to fourth index
		(i32.const 88)
		(i32.store8)
		
		(get_local $ptr)
		(i32.const 1)
		(i32.add) ;;stack holds pointer to the fifth index
		
		(i32.const 0x00636261) ;;NULL, c, b, a -> little endian
		(i32.store)
		
		(get_local $start_ptr)
		(call $_puts)
	)
	(start $_main)
)