;; ====== C ====== ;;

;; int main() {
;; 	unsigned int a = 0;
;; 	unsigned short *b = &a;
;; 	*b = -1;
;; 	view_mem("int");
;; 	return 0x00000000;
;; }

;; ====== wabt ====== ;;

(module
	(import "debug" "viewmemory" (func $_view_mem (param i32)))
	(import "debug" "dumpmemory" (func $_dump_mem (param i32)))
	(import "stdio" "puts"       (func $_puts (param i32)))
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0x00010000)) ;;end of memory: 65536 -> 64kb
	(data (i32.const 0x00000004) "int")

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
	
	(func $get_ptr (param $location i32) (result i32)
		(get_local $location)
		(get_global $stacktop)
		(i32.add)
	)

	(func $_main (result i32)
		(i32.const 8) (call $stack_alloc);; allocate space on the stack
		(i32.const 0) (call $get_ptr) (i32.const 0) (i32.store);; storing a on the stack
		(i32.const 4) (call $get_ptr) (i32.const 0) (call $get_ptr) (i32.store);; storing b on the stack
		(i32.const 4) (call $get_ptr) (i32.load) (i32.const -1) (i32.store16);; assigning to pointer location of b
		(i32.const 0x00000004) (call $_view_mem);; calling function _view_mem
		(i32.const 0x00000000);; Return
		(i32.const 8) (call $stack_free);; free stack reserved previously
	)

	(export "main" (func $_main))
)
