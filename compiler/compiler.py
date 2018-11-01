from pycparser import c_parser, c_ast
import os, subprocess

text = """
void ptr(int *x, int *y) {
	*x = *y;
}

int main() {
	int z = 0xDEADBEEF;
	int x = 0x12345678;
	int y = 0xDEADBEEF;
	int *memtype = "int";
	puts(memtype);
	
	view_mem(memtype);
	ptr(&y, &x);
	ptr(&z, &x);
	view_mem(memtype);
	return 0x00000000;
}

"""

module = """(module
	(import "debug" "viewmemory" (func $_view_mem (param i32)))
	(import "debug" "dumpmemory" (func $_dump_mem (param i32)))
	(import "stdio" "puts"       (func $_puts (param i32)))
	(memory (export "memory") 1)
	(global $stacktop (mut i32) (i32.const 0x00010000)) ;;end of memory: 65536 -> 64kb
"""

types = {
	"int": {"unsigned": False, "size": 4},
	"unsigned int" : {"unsigned": True, "size": 4},
}

data_pointer = 0x0004 #start after null
global_scope = {}
current_scope = {}
functions = {  #returns int? these are includes
	"view_mem": False,
	"dump_mem": False,
	"puts": False
}

def checkReturn(node):
	if " ".join(node.decl.type.type.type.names) != "void":
		return " (result i32)"
	return ""

def checkFuncArgs(node):
	try:
		out = ""
		for p in node.decl.type.args.params:
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
		if expr.type == "string":
			global module
			global data_pointer
			module += "\t(data (i32.const 0x%08x) %s)\n" % (data_pointer, expr.value)
			old_ptr = data_pointer
			data_pointer += len(expr.value)-1 #it looks like "test": in C it's len of 5, in here, it's len of 6
			return "(i32.const 0x%08x)" % (old_ptr)
		return "(i32.const %s)" % (expr.value)
			
	elif isinstance(expr, c_ast.FuncCall):
		return checkFuncCall(expr)
	elif isinstance(expr, c_ast.ID):
		return "%s (i32.load)" % (current_scope[expr.name])
	elif isinstance(expr, c_ast.BinaryOp):
		return "%s %s %s" % (checkVariable(expr.left), checkVariable(expr.right), checkBinaryOp(expr.op))
	elif isinstance(expr, c_ast.UnaryOp):
		if expr.op == "*":
			return "%s (i32.load) (i32.load)" % current_scope[expr.expr.name]
		elif expr.op == "&":
			return current_scope[expr.expr.name]
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
	
def checkFuncNeedsDrop(func):
	if functions[func.name.name]:
		return " (drop)"
	return ""

def to_wast():
	parser = c_parser.CParser()
	ast = parser.parse(text, filename='<none>')
	
	funcs = """
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

"""
	for node in ast.ext:
		if isinstance(node, c_ast.FuncDef):
			global current_scope
			current_scope = {}
			reserve_bytes = 0
			funcbody = ""
			
			funcname = node.decl.type.type.declname
			funcret = checkReturn(node)
			funcdef = "\t(func $_%s%s%s\n" % (funcname, checkFuncArgs(node), funcret)
			if funcret == "":
				functions[funcname] = False
			else:
				functions[funcname] = True
			try:
				for p in node.decl.type.args.params:
					current_scope[p.name] = "(i32.const %d) (call $get_ptr)" % (reserve_bytes)
					reserve_bytes += 4
					funcbody += "\t\t%s (get_local $%s) (i32.store);; storing parameter on the stack\n" % (current_scope[p.name], p.name)
			except AttributeError:
				pass
			for item in node.body.block_items:
				if isinstance(item, c_ast.Return):
					funcbody += "\t\t%s;; Return\n" % checkVariable(item.expr)
				elif isinstance(item, c_ast.Decl):
					current_scope[item.name] = "(i32.const %d) (call $get_ptr)" % (reserve_bytes)
					reserve_bytes += 4
					if item.init:
						funcbody += "\t\t%s %s (i32.store);; storing %s on the stack\n" % (current_scope[item.name], checkVariable(item.init), item.name)
				elif isinstance(item, c_ast.Assignment):
					funcbody += "\t\t"
					if item.op == "=":
						if isinstance(item.lvalue, c_ast.UnaryOp) and item.lvalue.op == "*":
							funcbody += "%s (i32.load) %s (i32.store);; assigning to pointer location of %s\n" % (current_scope[item.lvalue.expr.name], checkVariable(item.rvalue), item.lvalue.expr.name)
						else:
							funcbody += "%s %s (i32.store)\n" % (current_scope[item.lvalue.name], checkVariable(item.rvalue))
				elif isinstance(item, c_ast.FuncCall):
					funcbody += "\t\t%s%s;; calling function _%s\n" % (checkFuncCall(item), checkFuncNeedsDrop(item), item.name.name)
				else:
					print ">>> >>> %s" % item
			funcs += funcdef + ("\t\t(i32.const %s) (call $stack_alloc);; allocate space on the stack\n" % reserve_bytes) + funcbody + ("\t\t(i32.const %s) (call $stack_free);; free stack reserved previously\n" % reserve_bytes) + "\t)\n\n"
		else:
			print ">>> %s" % node
	funcs += "\t(export \"main\" (func $_main))\n)\n" #close module
	return module + funcs


if __name__ == "__main__":
	output = to_wast()
	#print output
	temp_file = "testing.wat"
	wasm_file = "..\\exec\\testing.wasm"
	with open(temp_file, "w") as f:
		f.write(";; ====== C ====== ;;\n")
		for x in text.splitlines():
			if x != "":
				f.write(";; " + x + "\n")
			else:
				f.write("\n")
		f.write(";; ====== wabt ====== ;;\n\n")
		f.write(output)

	if os.path.exists(wasm_file): os.remove(wasm_file)

	subprocess.call("to_wasm.bat %s %s" % (temp_file, wasm_file), shell=True)

