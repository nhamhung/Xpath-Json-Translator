from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes

from jsonpath_ng.ext import parse
from jsonpath_ng.ext.iterable import Len
import json
import pymongo
from bson.json_util import dumps
import sys
sys.path.append('../xpath')
from xpath import xpath_lexer

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
    return lr_recurse(tokens, "") + ".`len`" if len(tokens) > 0 else lr_recurse(tokens, "") + "`len`"

def extract_filter_condition(tokens):
    bracket_count = 1
    pos = 0
    for token in tokens:
        if token.type == '[':
            bracket_count += 1
        elif token.type == ']':
            bracket_count -= 1

        if bracket_count == 0:
            return pos
        pos += 1 

is_cond_filter = False

def lr_recurse(tokens, result):
    print(result + "\n")
    if not tokens:
        return result
    
    global is_cond_filter    

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
    elif token.value in ['>', '<', '<=', '>=', '=', '.', "'", ' ']:
        result += str(token.value)
        return lr_recurse(tokens, result)
    elif token.value in ['[']:
        closing_bracket_pos = extract_filter_condition(tokens)
        condition = tokens[0:closing_bracket_pos]
        if (len(condition) == 1 and condition[0].type == 'NUMBER'):
            num_pos = int(condition[0].value) -1
            tokens.pop(0)
            result += str(token.value)
            result += str(num_pos)
            is_cond_filter = False
            return lr_recurse(tokens, result)
        elif (len(condition) == 3 and condition[0].type == 'LAST'):
            tokens.pop(0) # pop 'last'
            tokens.pop(0) # pop brackets
            tokens.pop(0)
            result += str(token.value)
            result += '-1:'
            is_cond_filter = False
            return lr_recurse(tokens, result)
        else:
            result += str(token.value)
            result += "?(@."
            is_cond_filter = True
            return lr_recurse(tokens, result)
    elif token.type == 'AND':
        result += "&"
        return lr_recurse(tokens, result)
    elif token.value == '!=':
        result += "~="
        return lr_recurse(tokens, result)
    elif token.type == 'CHILD':
        return lr_recurse(tokens, result)
    elif token.type == 'DESCENDANT' :
        result += "."
        return lr_recurse(tokens, result)
    elif token.value == '::':
        return lr_recurse(tokens, result)
    elif token.value == ']':
        if (is_cond_filter):
            result += ')]'
        else:
            result += ']'
        return lr_recurse(tokens, result)

def evaluate_xpath_query(xpath_query, json_data):
    lexer = xpath_lexer.XpathLexer()
    xpath_tokens = list(lexer.tokenize(xpath_query))
    jsonpath_query = lr_recurse(xpath_tokens, "$")

    print("JSON QUERY: ", jsonpath_query)
    
    jsonpath_expr = parse(jsonpath_query)
    expr_result = jsonpath_expr.find(json_data)
    expr_boolean = [True if isinstance(r.path, Len) else False for r in expr_result]
    if all(expr_boolean):
        result = sum([match.value for match in expr_result])
    else:
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

    collection = test_db.get_collection('library')
    data = dumps(list(collection.find()))
    json_data = json.loads(data)

    # xpath_query = "/descendant::library/child::album/descendant::songs/child::song/descendant::title"
    # xpath_query = "/descendant::library/child::album[child::year=1998]/child::artists/descendant::artist[child::country='Indonesia']/child::name"
    # xpath_query = "count(/descendant::library/child::album[child::artists/descendant::artist/descendant::name='Anang Ashanty']/child::songs/descendant::song)"
    # xpath_query = "/descendant::library/child::album[count(descendant::songs/child::song)>=4]/child::title"
    
    # xpath_query = "//library/album//songs/song//title"
    # xpath_query = "//library/album[year=1998]/artists//artist[/country='Indonesia']/name"
    # xpath_query = "count(//library/album[artists//artist//name='Anang Ashanty']/songs//song)"
    # xpath_query = "//library/album[count(songs/song)>=4]/title"

    xpath_query = "//library/album[title='Separuh Jiwaku Pergi']//songs/song[3]"
    print(evaluate_xpath_query(xpath_query, json_data))

    # jsonpath_query = "$..library.album[?(@..songs.song.`len` >= 4)].title"
    # print(evaluate_jsonpath_query(jsonpath_query, json_data))

    # NOTES: XML does not have list, so to count, we must go to the child tag such as songs/song. For jsonpath just need to go the the level of the list such as songs
    # NOTES: For JsonPath, we can only filter on the array. For Xquery, we can filter on any tag
    # print(evaluate_jsonpath_query("$..bookbook.`len`", json_data))

    #NOTES : initially first album's artist is a list but the second and third album's artist is just a dictionary. Therefore our filtering query did not work. After we changed artist to list, it worked
    # strucutre of data must be consistent