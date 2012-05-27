from pyparsing import *

__all__ = ['parse_string']

# Define the ABC grammar

# Parse the ABC headers. Reference number and title are required, so they
# are separated from the other field headers.
optional_field_header = Word('COAMLQPZNGHKRBDFSI', exact=1)

ref_number = Keyword('X') + ':' + Word(nums).setResultsName('ref_number')
title = Keyword('T') + ':' + Word(printables).setResultsName('title')
header = optional_field_header + ':' + Word(printables)

headers = ref_number + title + header*(None, None)

note_length = (Literal('/')*(None, None) + Word(nums)) | Word('<>')
note = Optional(Word('^=_', max=2)) + Word("abcdefgABCDEFG") + Optional(Word(",'")) + Optional(note_length)
rest = Word('zxZ', exact=1) + Optional(note_length)
bar = (note | rest)*(1, None) + Optional('|')
line = Optional('|') + Optional(':') + bar*(1, None) + Optional(':') + Optional('|')
body = OneOrMore(line).setResultsName('body')

abc = headers + body

def parse_string(s):
    result = abc.parseString(s)
    return result
