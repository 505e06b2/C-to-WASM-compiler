from pycparser import c_parser, c_ast
import os, subprocess

text = """

int main() {
	int z = 60;
	int x = 100;
	int y = 200;
	return x + y + z;
}

"""

types = {
	"int": "i32",
	"long long": "i64",
	"long long int": "i64",
	"float": "f32",
	"double": "f64",
}

global_vars = {}
local_vars = {}

def checkReturn(names):
	if names != "":
		return " (result %s)" % types[names]
	return ""

def checkFuncArgs(args):
	try:
		out = ""
		for p in args.params:
			out += " (param $%s %s)" % (p.name, types["".join(p.type.type.names)])
		return out
	except AttributeError:
		return ""
	
def checkBinaryOp(op):
	if op == "+":
		return "(i32.add)"
	elif op == "-":
		return "(i32.sub)"
	return "<FIND OP>"

def checkVariable(expr):
	if isinstance(expr, c_ast.Constant):
		return "(%s.const %s)" % (types[expr.type], expr.value)
	elif isinstance(expr, c_ast.FuncCall):
		return checkFuncCall(expr)
	elif isinstance(expr, c_ast.ID):
		return "%s\n \t\t%s" % (local_vars[expr.name], "(i32.load)")
	elif isinstance(expr, c_ast.BinaryOp):
		return "%s %s %s" % (checkVariable(expr.left), checkVariable(expr.right), checkBinaryOp(expr.op))
	elif isinstance(expr, c_ast.UnaryOp):
		if isinstance(expr.expr, c_ast.Constant):
			return "(%s.const %s%s)" % (types[expr.expr.type], expr.op, expr.expr.value)
		return "<FIND UNARY>"
	else:
		print expr
		return "<FIND>"
		
def checkFuncCall(func):
	out = ""
	try:
		for p in func.args.exprs:
			out += "%s " % checkVariable(p)
	except AttributeError:
		pass
	return out + ("(call $_%s)" % func.name.name)

def to_wast():
	parser = c_parser.CParser()
	ast = parser.parse(text, filename='<none>')
	out = """(module
	(import "imports" "puts" (func $_puts (param i32)))
	(memory (export "memory") 1)
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

"""
	for node in ast.ext:
		if isinstance(node, c_ast.FuncDef):
			funcdef = "\t(func $_%s%s%s\n" % (node.decl.type.type.declname, checkFuncArgs(node.decl.type.args), checkReturn(" ".join(node.decl.type.type.type.names)) )
			funcbody = ""
			global local_vars
			local_vars = {}
			reserve_bytes = 0
			for item in node.body.block_items:
				if isinstance(item, c_ast.Return):
					funcbody += "\t\t%s\n" % checkVariable(item.expr)
				elif isinstance(item, c_ast.Decl):
					t = types[" ".join(item.type.type.names)]
					local_vars[item.name] = "(i32.const %d) (get_local $stack) (i32.add);; Get %s's pointer" % (reserve_bytes, item.name)
					reserve_bytes += 4
					if item.init:
						funcbody += "\t\t%s\n" % local_vars[item.name]
						funcbody += ("\t\t%s;; putting %s into wasm stack\n" % (checkVariable(item.init), item.name))
						funcbody += "\t\t(i32.store);; storing %s on the stack\n" % (item.name)
				elif isinstance(item, c_ast.Assignment):
					if item.op == "=":
						funcbody += "\t\t%s;;load %s from stack\n" % (checkVariable(item.rvalue), item.lvalue.name)
				else:
					print ">>> >>> %s" % item
			out += funcdef + ("\t\t(local $stack i32) (i32.const %s) (call $stack_alloc) (set_local $stack)\n" % reserve_bytes) + funcbody + "\t)\n\n"
		else:
			print ">>> %s" % node
	out += "\t(export \"main\" (func $_main))\n)\n" #close module
	return out


if __name__ == "__main__":
	output = to_wast()
	#print output
	temp_file = "testing.wat"
	wasm_file = "..\\exec\\testing.wasm"
	with open(temp_file, "w") as f:
		f.write(output)

	if os.path.exists(wasm_file): os.remove(wasm_file)

	subprocess.call("to_wasm.bat %s %s" % (temp_file, wasm_file), shell=True)

