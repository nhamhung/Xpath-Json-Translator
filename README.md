# CS4221-Project-10

## Translator

Direct translate from an XPath query to an equivalent JSONPath query on a MongoDB collection.

Consists of:
1. A Lexer to tokenize the XPath query
2. A Translator to convert the XPath query tokens into an equivalent JsonPath query
3. Evaluation of the JsonPath query on a MongoDB collection

- Test command: `python -m translator.xpath_translator`

## Evaluator

Build an AST for XPath and evaluate it on Json data

Consists of:
1. A Lexer to tokenize the XPath query
2. A Parser to build the AST
3. An Evaluator built into tree node to work with Json data

- Test command: `python -m xpath.test_xpath_evaluator`