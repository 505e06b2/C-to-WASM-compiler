from pycparser import c_parser, c_ast
import os, subprocess

text = """

int ptr(int *g) {
	*g = 0xFFFFFFFF;
	return 0xAABBCCDD;
}

int main() {
	int z = 0xDEADBEEF;
	int x = 0xDEADBEEF;
	int y = 0xDEADBEEF;
	int a = ptr(&x);
	return x + y + z;
}

"""

types = {
	"int": {"unsigned": False, "size": 4},
	"unsigned int" : {"unsigned": True, "size": 4},
}

global_vars = {}
local_vars = {}

def checkReturn(names):
	if names != "":
		return " (result i32)"
	return ""

def checkFuncArgs(args):
	try:
		out = ""
		for p in args.params:
			out += " (param $%s %s)" % (p.name, "i32")
		return out
	except AttributeError:
		return ""
	
def checkBinaryOp(op):
	if op == "+":
		return "(i32.add)"
	elif op == "-":
		return "(i32.sub)"
	return "<FIND OP>"

def checkVariable(expr, misc = None):
	if isinstance(expr, c_ast.Constant):
		return "(i32.const %s)" % (expr.value)
	elif isinstance(expr, c_ast.FuncCall):
		return checkFuncCall(expr)
	elif isinstance(expr, c_ast.ID):
		return "%s (i32.load)" % (local_vars[expr.name])
	elif isinstance(expr, c_ast.BinaryOp):
		return "%s %s %s" % (checkVariable(expr.left), checkVariable(expr.right), checkBinaryOp(expr.op))
	elif isinstance(expr, c_ast.UnaryOp):
		if expr.op == "*":
			#return "(i32.store)"
			return "ADD THIS FOR POINTERS"
		elif expr.op == "&":
			return local_vars[expr.expr.name]
		elif isinstance(expr.expr, c_ast.Constant):
			return "(i32.const %s%s)" % (expr.op, expr.expr.value)
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

"""
	for node in ast.ext:
		if isinstance(node, c_ast.FuncDef):
			global local_vars
			local_vars = {}
			reserve_bytes = 0
			funcbody = ""
			funcdef = "\t(func $_%s%s%s\n" % (node.decl.type.type.declname, checkFuncArgs(node.decl.type.args), checkReturn(" ".join(node.decl.type.type.type.names)) )
			try:
				for p in node.decl.type.args.params:
					local_vars[p.name] = "(i32.const %d) (get_global $stacktop) (i32.add)" % (reserve_bytes)
					reserve_bytes += 4
					funcbody += "\t\t%s (get_local $%s) (i32.store);; storing parameter on the stack\n" % (local_vars[p.name], p.name)
			except AttributeError:
				pass
			for item in node.body.block_items:
				if isinstance(item, c_ast.Return):
					funcbody += "\t\t%s;; Return\n" % checkVariable(item.expr)
				elif isinstance(item, c_ast.Decl):
					local_vars[item.name] = "(i32.const %d) (get_global $stacktop) (i32.add)" % (reserve_bytes)
					reserve_bytes += 4
					if item.init:
						funcbody += "\t\t%s %s (i32.store);; storing %s on the stack\n" % (local_vars[item.name], checkVariable(item.init), item.name)
				elif isinstance(item, c_ast.Assignment):
					funcbody += "\t\t"
					if item.op == "=":
						if isinstance(item.lvalue, c_ast.UnaryOp) and item.lvalue.op == "*":
							funcbody += "%s (i32.load) %s (i32.store);; assigning to pointer location\n" % (local_vars[item.lvalue.expr.name], checkVariable(item.rvalue))
						else:
							funcbody += "%s %s\n" % (checkVariable(item.rvalue), checkVariable(item.lvalue))
				else:
					print ">>> >>> %s" % item
			out += funcdef + ("\t\t(i32.const %s) (call $stack_alloc);; allocate space on the stack\n" % reserve_bytes) + funcbody + ("\t\t(i32.const %s) (call $stack_free);; free stack reserved previously\n" % reserve_bytes) + "\t)\n\n"
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

