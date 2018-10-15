(module
	(memory $mem 1)
	(global $stacktop i32 (i32.const 0xFA00))
	(func $main (result i32)
		(i32.const 10)
	)
	(export "main" (func $main))
)