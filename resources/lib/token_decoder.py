import re
import math


# the + in the beginning parses text to a number
# a [] converts everything before into text -> therefore everythin before *10 or *100 or *1000
# '(+((!+[]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![]+[])+(!+[]+!![]+[])))>>(!+[]+!![]+!![]+!![]+!![]+!![]+!![])'
# '(+((1+1+1+1+1+10)+(1+1+1+1+1+1+1+1+10)+(+10)+(1+10)))>>(1+1+1+1+1+1+1)'
# 0 is a marker for times 10 or more
# expands to
# '(+((1+1+1+1+1+1)*1000+(1+1+1+1+1+1+1+1+1)*100+(+1)*10+(1+1)*1))>>(1+1+1+1+1+1+1)'


class TokenDecoder:
    #_parentheses_group_regex = r"(\(\d+\))"
    _outer_parentheses_group_regex = r"\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)"
    _lines_regex_template = r"{}\(([^\,a]+)\)"
    TOKEN_COOKIE_NAME = 'reqkey'

    def __init__(self):
        pass

    @staticmethod
    def get_token(send_method):
        req = send_method('https://9anime.is/token?v1')
        lines = TokenDecoder.get_lines_to_decode(req.text)
        chars = map(lambda x: TokenDecoder.decode_as_char(x), lines)
        result = ''.join(chars)
        return result

    @staticmethod
    def get_lines_to_decode(text):
        function_name = TokenDecoder._find_function_name(text)
        lines_regex = TokenDecoder._lines_regex_template.format(function_name)
        matches = list(re.findall(lines_regex, text))
        return matches

    @staticmethod
    def decode_as_int(text):
        return TokenDecoder._get_token_number(text)

    @staticmethod
    def decode_as_char(text):
        num = TokenDecoder.decode_as_int(text)
        return chr(num)

    @staticmethod
    def _get_token_number(text):
        # !![] should be +!![] but im using the extra + so all 1 get accumulated
        # will result in (1+1+1+1+1+1) instead of (111111)
        replaced = text.replace('!+[]', '1').replace('!![]', '1').replace('+[]', '0')
        expanded = TokenDecoder._recursive_token_multiplier(replaced)
        return eval(expanded)

    @staticmethod
    def _recursive_token_multiplier(text):
        matches = re.findall(TokenDecoder._outer_parentheses_group_regex, text)
        result = text
        for valNum, val in enumerate(matches):
            if not val.endswith('0)'):
                result = result.replace(val, '(' + TokenDecoder._recursive_token_multiplier(TokenDecoder._remove_parenthesis(val)) + ')', 1)
            else:
                multiplier = int(math.pow(10, len(matches) - 1 - valNum))
                result = result.replace(val, val.replace('0)', ')*{}'.format(multiplier)), 1)

        return result

    @staticmethod
    def _remove_parenthesis(text):
        if text.startswith('(') and text.endswith(')'):
            return (text[1:])[:-1]
        return text


    @staticmethod
    def _find_function_name(text):
        start_of = text.find('=function(')
        return text[start_of - 1]

