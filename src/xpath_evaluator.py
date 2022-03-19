from jsonpath_ng.ext import parse
from xpath_lexer import *
import json
import pymongo
from bson.json_util import dumps

def extract_count(tokens):
    bracket_count = 1
    pos = 0
    for token in tokens:
        if token.type == '(':
            bracket_count += 1
        elif token.type == ')':
            bracket_count -= 1

        if bracket_count == 0:
            return pos
        pos += 1

def parse_count_condition(tokens):
    if len(tokens) > 2 and tokens[-1].type == 'ID' and tokens[-2].value == '/':
        tokens.pop()
        tokens.pop()
    
    return lr_recurse(tokens, "") + ".`len`" if len(tokens) > 0 else lr_recurse(tokens, "") + "`len`"
    

def lr_recurse(tokens, result):
    if not tokens:
        return result
    
    token = tokens.pop(0)
    if token.value == '/':
        result += '.'
        return lr_recurse(tokens, result)
    elif token.value == '//':
        result += '..'
        return lr_recurse(tokens, result)
    elif token.type in ['ID', 'NUMBER']:
        result += str(token.value)
        return lr_recurse(tokens, result)
    elif token.type == 'COUNT':
        tokens.pop(0)
        closing_bracket_pos = extract_count(tokens)
        count_condition_tokens = tokens[0:closing_bracket_pos]
        result += parse_count_condition(count_condition_tokens)
        return lr_recurse(tokens[closing_bracket_pos+1:], result)
    elif token.value in ['>', '<', '<=', '>=', ']']:
        result += str(token.value)
        return lr_recurse(tokens, result)
    elif token.value in ['[']:
        result += str(token.value)
        result += "?"
        return lr_recurse(tokens, result)
    elif token.type == 'AND':
        result += "&"
        return lr_recurse(tokens, result)

def evaluate_xpath_query(xpath_query, json_data):
    lexer = XpathLexer()
    xpath_tokens = list(lexer.tokenize(xpath_query))
    jsonpath_query = lr_recurse(xpath_tokens, "$")
    print("JSON QUERY: ", jsonpath_query)
    jsonpath_expr = parse(jsonpath_query)
    result = [match.value for match in jsonpath_expr.find(json_data)]
    return result

def evaluate_jsonpath_query(jsonpath_query, json_data):
    jsonpath_expr = parse(jsonpath_query)
    result = [match.value for match in jsonpath_expr.find(json_data)]
    return result

if __name__ == '__main__':
    db_name='test'
    test_client = pymongo.MongoClient('mongodb://localhost:27017/')
    test_db = test_client[db_name]

    collection = test_db.get_collection('bookstore')
    data = dumps(list(collection.find()))
    json_data = json.loads(data)

    # xpath_query = "count(//store/book[price > 10 and price < 20])"
    # xpath_query = "//store[count(book)>2]"
    xpath_query = "//store/book[price>10]"
    # lexer = XpathLexer()
    # print(lr_recurse(list(lexer.tokenize(xpath_query)), "$"))
    print(evaluate_xpath_query(xpath_query, json_data))

    # NOTES: XML does not have list, so to count, we must go to the child tag such as songs/song. For jsonpath just need to go the the level of the list such as songs
    # NOTES: For JsonPath, we can only filter on the array. For Xquery, we can filter on any tag
    # print(evaluate_jsonpath_query("$..bookbook.`len`", json_data))
