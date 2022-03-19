# An XPath query evaluator to work on Json data directly

Consists of:
1. A Lexer to tokenize the XPath query
2. A Translator to convert the XPath query tokens into an equivalent JsonPath query
3. Evaluation of the JsonPath query on a MongoDB collection
