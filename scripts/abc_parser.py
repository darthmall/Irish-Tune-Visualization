from pyparsing import *

__all__ = ['parse_string']

# Define the ABC grammar

# Parse the ABC headers. Reference number and title are required, so they
# are separated from the other field headers.
digits = Word(nums)
text = Word(printables) + ZeroOrMore(White(ws=" \t") + Word(printables))
fraction = digits + "/" + digits

complex_meter = "(" + digits + OneOrMore("+" + digits) + ")"
meter_fraction = (complex_meter | digits) + "/" + digits
meter = Keyword("C") | Keyword("C|") | Keyword("none") | meter_fraction

# FIXME: Needs to support optional quoted strings indicating tempo, e.g. "Andante"
beat = fraction + Optional("=" + digits)
tempo = beat + ZeroOrMore(White(ws=" \t") + beat)

tonic = Word("ABCDEFG", exact=1)
key_accidental = Literal("#") | Literal("b")
mode = Literal("m") + Optional("in") | Literal("Mix") | Literal("Dor") | Literal("Phr") | Literal("Lyd") | Literal("Loc")
key = tonic + Optional(key_accidental) + Optional(mode)

field_ref_number = Keyword("X:") + digits.setResultsName("ref_number")
field_title = Keyword("T:") + text.setResultsName("title")
field_composer = Keyword("C:") + text.setResultsName("composer")
field_origin = Keyword("O:") + (text + ZeroOrMore(";" + text)).setResultsName("origin")
field_meter = Keyword("M:") + meter.setResultsName("meter")
field_tempo = Keyword("Q:") + tempo.setResultsName("tempo")
field_note_length = Keyword("L:") + fraction.setResultsName("note_length")
field_rhythm = Keyword("R:") + text.setResultsName("rhythm")
field_key = Keyword("K:") + key.setResultsName("key")

optional_fields = field_composer | field_origin | field_note_length | field_meter | field_tempo | field_rhythm

abc_header = field_ref_number + field_title + ZeroOrMore(optional_fields) + field_key

abc_tune = abc_header

def parse_string(s):
    result = abc_tune.parseString(s)
    return result
