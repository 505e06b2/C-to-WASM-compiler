(module
	(func $add (param $left i32) (param $right i32) (result i32)
		(return (get_local $left) (get_local $right) (i32.add) (i32.const 10) (i32.add))
	)

	(func $main (result i32)
		(local $z i32)
		(local $r i32)
		(i32.const 60) (set_local $z)
		(get_local $z) (i32.const 1) (call $add) (i32.const 2) (i32.add) (set_local $r)
		(return (get_local $r))
	)

	(export "main" (func $main))
)
