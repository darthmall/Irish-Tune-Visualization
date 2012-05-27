from pyparsing import *

__all__ = ['parse_string']

# Define the ABC grammar

# Parse the ABC headers. Reference number and title are required, so they
# are separated from the other field headers.

# Grammar found here: http://mit.edu/6.005/www/fa08/projects/abcPlayer/assignment_files/abc_subset_bnf.txt
text = Word(printables) | White(ws=" \t")
digit = Word(nums)

comment = "%" + text
end_of_line = comment

barline = Literal("|") | Literal("||") | Literal("[|") | Literal("|]") | Literal(":|") | Literal("|:") | Literal("::")
nth_repeat = Literal("[1") | Literal("[2")

accidental = Literal("^") | Literal("^^") | Literal("_") | Literal("__") | Literal("=")
base_note = Word("abcdefgABCDEFG")
rest = Word("zZ")

key_base_note = Word("ABCDEFG")
key_accidental = Literal("#") | Literal("b")
mode = Literal("m") | Literal("Min") | Literal("Mix") | Literal("Dor") | Literal("Phr") | Literal("Lyd") | Literal("Loc")
key_note = key_base_note + Optional(key_accidental)
key = key_note + Optional(mode)

tempo = OneOrMore(nums)

octave = OneOrMore("'") | OneOrMore(",")
pitch = Optional(accidental) + base_note + Optional(octave)
note_or_rest = pitch | rest
note_length = Optional(OneOrMore(digit)) + Optional("/" + Optional(OneOrMore(digit)))
note_length_strict = digit*(1, None) + "/" + digit*(1, None)
note = note_or_rest + Optional(note_length)
multi_note = "[" + OneOrMore(note) + "]"
note_element = note | multi_note

tuplet_spec = "(" + digit
tuplet_element = tuplet_spec + OneOrMore(note_element)

meter_fraction = digit*(1, None) + "/" + digit*(1, None)
meter = Literal("C") | Literal("C|") | meter_fraction

field_number = "X:" + OneOrMore(digit).setResultsName("ref_number")
field_title = "T:" + Optional(text.setResultsName("title"))
field_composer = "C:" + text.setResultsName("composer")
field_default_length = "L:" + note_length_strict.setResultsName("note_length")
field_meter = "M:" + meter.setResultsName("meter")
field_tempo = "Q:" + tempo.setResultsName("tempo")
field_voice = "V:" + text.setResultsName("voice")
field_key = "K:" + key.setResultsName("key")

other_fields = field_composer | field_default_length | field_meter | field_tempo | field_voice | field_key | comment

mid_tune_field = field_voice

abc_header = field_number + ZeroOrMore(comment) + field_title + ZeroOrMore(other_fields)

element = note_element | tuplet_element | barline | nth_repeat | Literal(" ")
abc_line = OneOrMore(element) | mid_tune_field | comment
abc_music = OneOrMore(abc_line).setResultsName("body", True)

abc_tune = abc_header + abc_music

def parse_string(s):
    result = abc_tune.parseString(s)
    return result
