;; ====== C ====== ;;

;; void ptr(int *x, int *y) {
;; 	*x = *y;
;; }

;; int main() {
;; 	int z = 0xDEADBEEF;
;; 	int x = 0x12345678;
;; 	int y = 0xDEADBEEF;
;; 	int *memtype = "int";
;; 	puts(memtype);
;; 	
;; 	view_mem(memtype);
;; 	ptr(&y, &x);
;; 	ptr(&z, &x);
;; 	view_mem(memtype);
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

	(func $_ptr (param $x i32) (param $y i32)
		(i32.const 8) (call $stack_alloc);; allocate space on the stack
		(i32.const 0) (call $get_ptr) (get_local $x) (i32.store);; storing parameter on the stack
		(i32.const 4) (call $get_ptr) (get_local $y) (i32.store);; storing parameter on the stack
		(i32.const 0) (call $get_ptr) (i32.load) (i32.const 4) (call $get_ptr) (i32.load) (i32.load) (i32.store);; assigning to pointer location of x
		(i32.const 8) (call $stack_free);; free stack reserved previously
	)

	(func $_main (result i32)
		(i32.const 16) (call $stack_alloc);; allocate space on the stack
		(i32.const 0) (call $get_ptr) (i32.const 0xDEADBEEF) (i32.store);; storing z on the stack
		(i32.const 4) (call $get_ptr) (i32.const 0x12345678) (i32.store);; storing x on the stack
		(i32.const 8) (call $get_ptr) (i32.const 0xDEADBEEF) (i32.store);; storing y on the stack
		(i32.const 12) (call $get_ptr) (i32.const 0x00000004) (i32.store);; storing memtype on the stack
		(i32.const 12) (call $get_ptr) (i32.load) (call $_puts);; calling function _puts
		(i32.const 12) (call $get_ptr) (i32.load) (call $_view_mem);; calling function _view_mem
		(i32.const 8) (call $get_ptr) (i32.const 4) (call $get_ptr) (call $_ptr);; calling function _ptr
		(i32.const 0) (call $get_ptr) (i32.const 4) (call $get_ptr) (call $_ptr);; calling function _ptr
		(i32.const 12) (call $get_ptr) (i32.load) (call $_view_mem);; calling function _view_mem
		(i32.const 0x00000000);; Return
		(i32.const 16) (call $stack_free);; free stack reserved previously
	)

	(export "main" (func $_main))
)
