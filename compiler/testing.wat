(module
	(func $extra (result i32)
		(return (i32.const 2))
	)

	(func $main (result i32)
		(local $r i32)
		(i32.const -1) (i32.const 2) (i32.add) (set_local $r)
		(return (get_local $r))
	)

	(export "main" (func $main))
)
