from pycparser import c_parser, c_ast
import os, subprocess

text = """

int extra() {
	return 2;
}

int main() {
	int r = -1 + 2;
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
		return "(call $%s)" % expr.name.name
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

def to_wast():
	parser = c_parser.CParser()
	ast = parser.parse(text, filename='<none>')
	out = "(module\n"
	for node in ast.ext:
		if isinstance(node, c_ast.FuncDef):
			out += "\t(func $%s%s\n" % (node.decl.type.type.declname, checkReturn(" ".join(node.decl.type.type.type.names)) )
			for item in node.body.block_items:
				if isinstance(item, c_ast.Return):
					out += "\t\t(return %s)\n" % checkVariable(item.expr)
				elif isinstance(item, c_ast.Decl):
					t = types[" ".join(item.type.type.names)]
					out += "\t\t(local $%s %s)\n" % (item.name, t)
					if item.init:
						out += "\t\t%s (set_local $%s)\n" % (checkVariable(item.init), item.name)
				elif isinstance(item, c_ast.Assignment):
					if item.op == "=":
						out += "\t\t%s (set_local $%s)\n" % (checkVariable(item.rvalue), item.lvalue.name)
				else:
					print ">>> >>> %s" % item
			out += "\t)\n\n"
		else:
			print ">>> %s" % node
	out += "\t(export \"main\" (func $main))\n)\n" #close module
	return out


if __name__ == "__main__":
	output = to_wast()
	#print output
	temp_file = "testing.wat"
	wasm_file = "..\\server\\testing.wasm"
	with open(temp_file, "w") as f:
		f.write(output)

	if os.path.exists(wasm_file): os.remove(wasm_file)

	subprocess.call("to_wasm.bat %s %s" % (temp_file, wasm_file), shell=True)

