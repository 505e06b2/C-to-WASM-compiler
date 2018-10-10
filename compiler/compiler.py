from pycparser import c_parser, c_ast
import os, subprocess

text = """

int add(int left, int right) {
	return left + right + 10;
}

int main() {
	int z = 60;
	int r = add(z,1) + 2;
	return r;
}

"""

types = {
	"int": "i32",
	"long long": "i64",
	"long long int": "i64",
	"float": "f32",
	"double": "f64",
}

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
		return "(get_local $%s)" % expr.name
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
	return out + ("(call $%s)" % func.name.name)

def to_wast():
	parser = c_parser.CParser()
	ast = parser.parse(text, filename='<none>')
	out = "(module\n"
	for node in ast.ext:
		if isinstance(node, c_ast.FuncDef):
			funcdef = "\t(func $%s%s%s\n" % (node.decl.type.type.declname, checkFuncArgs(node.decl.type.args), checkReturn(" ".join(node.decl.type.type.type.names)) )
			funcbody = ""
			for item in node.body.block_items:
				if isinstance(item, c_ast.Return):
					funcbody += "\t\t(return %s)\n" % checkVariable(item.expr)
				elif isinstance(item, c_ast.Decl):
					t = types[" ".join(item.type.type.names)]
					funcdef += "\t\t(local $%s %s)\n" % (item.name, t)
					if item.init:
						funcbody += "\t\t%s (set_local $%s)\n" % (checkVariable(item.init), item.name)
				elif isinstance(item, c_ast.Assignment):
					if item.op == "=":
						funcbody += "\t\t%s (set_local $%s)\n" % (checkVariable(item.rvalue), item.lvalue.name)
				else:
					print ">>> >>> %s" % item
			out += funcdef + funcbody + "\t)\n\n"
		else:
			print ">>> %s" % node
	out += "\t(export \"main\" (func $main))\n)\n" #close module
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

