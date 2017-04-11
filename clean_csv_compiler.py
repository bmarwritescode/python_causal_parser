import sys


################################################################
#	LEXER
################################################################

# Token Types

# Maybe add type, all, Causes, CONT ???
(LPAREN, RPAREN, COMMA, LBRACK, RBRACK, LCURLY, RCURLY, SEMI,
	EQUALS, AND, OR, COLON, ID, INTEGER, CAUSES, DOT, QUOTE, 
	RULES, TYPE, ALL, CONT, IF, EOF) = (
	'LPAREN', 'RPAREN', 'COMMA', 'LBRACK', 'RBRACK', 'LCURLY',
	'RCURLY', 'SEMI', 'EQUALS', 'AND', 'OR', 'COLON', 'ID', 
	'INTEGER', 'CAUSES', 'DOT', 'QUOTE', 'RULES', 'TYPE', 
	'ALL', 'CONT', 'IF', 'EOF'
)

class Token(object):
	def __init__(self, type, value):
		# token type: VAR, COMMA, CAUSES, etc.
		self.type = type
		# token value: int, float, string, None
		self.value = value

	def __str__(self):

		return 'Token({type}, {value})'.format(
			type = self.type,
			value = repr(self.value)
		)

	def __repr__(self):
		return self.__str__()

RESERVED_KEYWORDS = {
	'RULES': Token('RULES', 'RULES'),
	'TYPE':   Token('TYPE', 'TYPE'),
	'ALL':   Token('ALL', 'ALL'),
	'CONT':   Token('CONT', 'CONT'),
	'if': Token('IF', 'IF'),
}

class Lexer(object):
	def __init__(self, text):
		# input code
		self.text = text
		# index in self.text
		self.pos = 0
		self.current_char = self.text[self.pos]

	def error(self):
		raise Exception('Invalid character: {c}'.format(
			c = self.current_char
		))

	def advance(self):
		self.pos += 1
		if self.pos > len(self.text) - 1:
			self.current_char = None
		else:
			self.current_char = self.text[self.pos]

	def skip_whitespace(self):
		while self.current_char is not None and self.current_char.isspace():
			self.advance()

	def integer(self):
		result = ''
		while self.current_char is not None and self.current_char.isdigit():
			result += self.current_char
			self.advance()
		return int(result)

	def peek(self):
		peek_pos = self.pos + 1
		if peek_pos > len(self.text) - 1:
			return None
		else:
			return self.text[peek_pos]

	def _id(self):
		result = ''
		while self.current_char is not None and self.current_char.isalnum():
			result += self.current_char
			self.advance()

		token = RESERVED_KEYWORDS.get(result, Token(ID, result))
		return token

	def get_next_token(self):

		while self.current_char is not None:

			if self.current_char.isspace():
				self.skip_whitespace()
				continue

			if self.current_char.isalpha():
				return self._id()

			if self.current_char.isdigit():
				return Token(INTEGER, self.integer())

			if self.current_char == ':' and self.peek() == '=':
				self.advance()
				self.advance()
				return Token(CAUSES, ':=')

			if self.current_char == ';':
				self.advance()
				return Token(SEMI, ';')									

			if self.current_char == '(':
				self.advance()
				return Token(LPAREN, '(')			

			if self.current_char == ')':
				self.advance()
				return Token(RPAREN, ')')			

			if self.current_char == '[':
				self.advance()
				return Token(LBRACK, '[')			

			if self.current_char == ']':
				self.advance()
				return Token(RBRACK, ']')			

			if self.current_char == ',':
				self.advance()
				return Token(COMMA, ',')			

			if self.current_char == '{':
				self.advance()
				return Token(LCURLY, '{')			

			if self.current_char == '}':
				self.advance()
				return Token(RCURLY, '}')			

			if self.current_char == '=':
				self.advance()
				return Token(EQUALS, '=')			

			if self.current_char == '{':
				self.advance()
				return Token(LCURLY, '{')			

			if self.current_char == '&' and self.peek() == '&':
				self.advance()
				self.advance()
				return Token(AND, '&&')			

			if self.current_char == '|' and self.peek() == '|':
				self.advance()
				self.advance()
				return Token(AND, '||')			

			if self.current_char == ':':
				self.advance()
				return Token(COLON, ':')			

			if self.current_char == '.':
				self.advance()
				return Token(DOT, '.')			

			if self.current_char == '\'':
				self.advance()
				return Token(QUOTE, '\'')			

			self.error()

		return Token(EOF, None)

################################################################
#	Parser
################################################################
class AST(object):
	pass

class Int(AST):
	def __init__(self):
		self.digits = []

class Flt(AST):
	def __init__(self, left, right):
		self.left = left
		self.right = right

class Literal(AST):
	def __init__(self, name):
		self.name = name

class Boolean(AST):
	def __init__(self, e1, e2):
		self.e1 = e1
		self.e2 = e2

class BoolExpr(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right

class Args(AST):
	def __init__(self):
		self.children = []

class Act(AST):
	def __init__(self, var, args):
		self.var = var
		self.args = args

class Acts(AST):
	def __init__(self):
		self.children = []

class Caus(AST):
	def __init__(self, act, acts):
		self.act = act
		self.acts = acts

class Cond(AST):
	def __init__(self, boolean):
		self.boolean = boolean

class Stmt(AST):
	def __init__(self, cond, caus):
		self.cond = cond
		self.caus = caus

class Stmts(AST):
	def __init__(self):
		self.children = []

class Var(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value

class NoOp(AST):
	pass

class Parser(object):
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()

	def error(self):
		raise Exception('Invalid syntax: {token}'.format(
			token = self.current_token
		))

	def eat(self, token_type):
		if self.current_token.type == token_type:
			# DEBUGGING
			print self.current_token
			self.current_token = self.lexer.get_next_token()
		else:
			# DEBUGGING
			print "Token Type: ", token_type			
			self.error()

	def program(self):
		# program -> RULES LCURLY stmts RCURLY
		self.eat(RULES)
		self.eat(LCURLY)
		node = self.stmts()
		self.eat(RCURLY)
		return node

	def stmts(self):
		# stmts ->   stmt
		#		   | stmt SEMI stmts
		node = self.stmt()

		root = Stmts()

		root.children.append(node)

		while self.current_token.type == SEMI:
			self.eat(SEMI)
			root.children.append(self.stmt())

		return root

	def stmt(self):
		# stmt -> cond caus
		node1 = self.cond()
		node2 = self.caus()

		root = Stmt(cond=node1, caus=node2)

		return root

	def cond(self):
		# cond -> IF LPAREN boolsAnd RPAREN COLON
		#		  | empty		    
		print "COND"
		if self.current_token.type == IF:
			self.eat(IF)
			self.eat(LPAREN)
			node1 = self.boolsAnd()
			self.eat(RPAREN)
			self.eat(COLON)

			root = Cond(boolean=node1)
		else:
			root = self.empty()

		return root

	def caus(self):
		# caus -> act CAUSES acts
		print "CAUS"
		node1 = self.act()
		self.eat(CAUSES)
		node2 = self.acts()

		root = Caus(act=node1, acts=node2)

		return root

	def acts(self):
		# acts ->   act COMMA acts
		#	 	  | act
		print "ACTS"
		node = self.act()

		root = Acts()

		root.children.append(node)

		while self.current_token.type == COMMA:
			self.eat(COMMA)
			root.children.append(self.act())

		return root

	def act(self):
		# act -> var LPAREN args RPAREN
		print "ACT"
		node1 = self.var()
		self.eat(LPAREN)
		node2 = self.args()
		self.eat(RPAREN)

		root = Act(var=node1, args=node2)

		return root

	def args(self):
		# args ->   var COMMA args
		#		  | var
		node = self.var()

		root = Args()

		root.children.append(node)

		while self.current_token.type == COMMA:
			self.eat(COMMA)
			root.children.append(self.var())

		return root

	def boolsAnd(self):
		# boolsAnd -> boolsOr (AND boolsOr)*
		node = self.boolsOr()

		while self.current_token.type == AND:
			token = self.current_token
			self.eat(AND)

			node = BoolExpr(left=node, op=token, right=self.boolsOr())

		return node

	def boolsOr(self):
		# boolsOr -> boolean (OR boolean)*
		node = self.boolean()

		while self.current_token.type == OR:
			token = self.current_token
			self.eat(OR)

			node = BoolExpr(left=node, op=token, right=self.boolean())

		return node

	def boolean(self):
		# boolean -> expr EQUALS expr
		node1 = self.expr()
		self.eat(EQUALS)
		node2 = self.expr()

		root = Boolean(e1=node1, e2=node2)

		return root

	def expr(self):
		# expr ->   var
		#		  | ALL LPAREN var RPAREN
		#		  | TYPE LPAREN var RPAREN
		#		  | QUOTE var QUOTE
		#		  | LBRACK args RBRACK
		#		  | LPAREN boolsAnd RPAREN
		if self.current_token.type == ALL:		
			self.eat(ALL)
			self.eat(LPAREN)
			node = self.var()
			self.eat(RPAREN)
		elif self.current_token.type == TYPE:		
			self.eat(TYPE)
			self.eat(LPAREN)
			node = self.var()
			self.eat(RPAREN)
		elif self.current_token.type == QUOTE:					
			self.eat(QUOTE)
			node1 = self.var()
			node = Literal(name=node1)
			self.eat(QUOTE)
		elif self.current_token.type == LBRACK:		
			self.eat(LBRACK)
			node = self.args()
			self.eat(RBRACK)
		elif self.current_token.type == LPAREN:		
			self.eat(LPAREN)
			node = self.boolsAnd
			self.eat(RPAREN)
		else:
			node = self.var()

		return node

	def var(self):
		# variable ->   ID
		#             | integer
		#             | integer DOT integer    (This is a float)
		#			  | DOT integer            (This is a float)
		print "VAR"
		if self.current_token.type == INTEGER:
			node1 = self.integer()
			if self.current_token.type == DOT:
				self.eat(DOT)
				node2 = self.integer()
				node = Flt(left=node1, right=node2)
			else:
				node = node1
		elif self.current_token.type == DOT:
			node1 = Int()
			self.eat(DOT)
			node2 = self.integer()
			node = Float(left=node1, right=node2)
		else:				
			node = Var(self.current_token)
			self.eat(ID)
		
		return node

	def integer(self):
		# integer ->   INTEGER integer
		#            | INTEGER

		node = self.current_token

		root = Int()

		root.digits.append(node)

		while self.current_token.type == INTEGER:
			root.digits.append(self.current_token)
			self.eat(INTEGER)

		return root

	def empty(self):
		return NoOp()

	def parse(self):
		node = self.program()

		if self.current_token.type != EOF:
			self.error()

		return node

################################################################
#	Interpreter
################################################################

class NodeVisitor(object):
	def visit(self, node):
		method_name = 'visit_'+type(node).__name__
		visitor = getattr(self, method_name, self.generic_visit)
		return visitor(node)

	def generic_visit(self, node):
		raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):

	GLOBAL_SCOPE = {}

	def __init__(self, parser):
		self.parser = parser

	def visit_Literal(self, node):
		return node.name

	def visit_Boolean(self, node):
		return self.visit(node.e1) + "=" + self.visit(node.e2)

	def visit_BoolExpr(self, node):
		if node.op.type == AND:
			return self.visit(node.left) + "&&" + self.visit(node.right)
		elif node.op.type == OR:
			return self.visit(node.left) + "||" + self.visit(node.right)

	def visit_Args(self, node):
		result = ''
		for child in node.children:
			result += self.visit(child)

		return result

	def visit_Act(self, node):
		return self.visit(node.var) + '(' + self.visit(node.args) + ')'

	def visit_Acts(self, node):
		result = ''
		for child in node.children:
			result += self.visit(child)

		return result

	def visit_Caus(self, node):
		return self.visit(node.act) + ':=' + self.visit(node.acts)

	def visit_Cond(self, node):
		return 'if (' + self.visit(node.boolean) + '):'

	def visit_Stmt(self, node):
		return self.visit(node.cond) + self.visit(node.caus)
		def __init__(self, cond, caus):
			self.cond = cond
			self.caus = caus

	def visit_Stmts(self, node):
		result = ''
		for child in node.children:
			result += self.visit(child)

		return result

	def visit_Var(self, node):
		return node.value

	def visit_NoOp(self, node):
		pass

	def interpret(self):
		tree = self.parser.parse()
		return self.visit(tree)

def main():
	text = open(sys.argv[1], 'r').read()

	lexer = Lexer(text)
	parser = Parser(lexer)
	interpreter = Interpreter(parser)
	result = interpreter.interpret()
	print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
   main();
