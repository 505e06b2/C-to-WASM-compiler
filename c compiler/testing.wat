(module
	(func $extra (result i32)
		(return (i32.const 2))
	)

	(func $main (result i32)
		(local $r i32)
		(call $extra) (set_local $r)
		(return (get_local $r))
	)

	(export "main" (func $main))
)
