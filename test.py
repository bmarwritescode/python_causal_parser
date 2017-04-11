from clean_csv_compiler import Lexer
from clean_csv_compiler import Parser
from clean_csv_compiler import Interpreter

def lexer_print_tokens(lexer):
	token = lexer.get_next_token()
	while token.type != 'EOF':
		print token
		token = lexer.get_next_token()

def main():
	print "TESTING..."
	text = open('causes.txt', 'r').read()
	#text = open(sys.argv[1], 'r').read()

	print "TESTING LEXER"
	lexer = Lexer(text)

	# lexer_print_tokens(lexer)

	print "TESTING PARSER"
	parser = Parser(lexer)

	print "TESTING INTERPRETER"
	interpreter = Interpreter(parser)
	result = interpreter.interpret()

	print result

if __name__ == '__main__':
   main();

