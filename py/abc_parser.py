from pyparsing import *

__all__ = ['parse_string']

def debugException(instring, loc, expr, exc):
    print("oops")
    print(instring[col(loc, instring)])

# Define the ABC grammar

# Parse the ABC headers. Reference number and title are required, so they
# are separated from the other field headers.
digits = Word(nums)
text = Word(printables) + ZeroOrMore(White(ws=" \t").suppress() + Word(printables))
fraction = digits + "/" + digits

comment = "%" + text
end_of_line = Optional(comment) + White(ws="\n\r")

complex_meter = "(" + digits + OneOrMore("+" + digits) + ")"
meter_fraction = (complex_meter | digits) + "/" + digits
meter = Keyword("C") | Keyword("C|") | Keyword("none") | meter_fraction

# FIXME: Needs to support optional quoted strings indicating tempo, e.g. "Andante"
beat = fraction + Optional("=" + digits)
tempo = beat + ZeroOrMore(White(ws=" \t") + beat)

key = Word(printables)

field_ref_number = Keyword("X:") + digits.setResultsName("ref_number")
field_title = Keyword("T:") + text.setResultsName("title")
field_composer = Keyword("C:") + text.setResultsName("composer")
field_origin = Keyword("O:") + (text + ZeroOrMore(";" + text)).setResultsName("origin")
field_meter = Keyword("M:") + meter.setResultsName("meter")
field_tempo = Keyword("Q:") + tempo.setResultsName("tempo")
field_note_length = Keyword("L:") + fraction.setResultsName("note_length")
field_rhythm = Keyword("R:") + text.setResultsName("rhythm")
field_key = Keyword("K:") + key.setResultsName("key")
field_parts = Keyword("P:") + text.setResultsName("parts")

optional_fields = field_composer | field_origin | field_note_length | field_meter | field_tempo | field_rhythm | field_parts | field_key

abc_header = field_ref_number + field_title + ZeroOrMore(optional_fields)

base_note = Word("abcdefgABCDEFG")
octave = OneOrMore(",") | OneOrMore("'")
accidental = Word("^", max=2) | Word("_", max=2) | Literal("=")
pitch = Optional(accidental).setName('accidental') + base_note.setName('base_note') + Optional(octave).setName('octave')
note_length = digits | Word("/") | "/" + digits
broken_rhythm = Word("<>", exact=1)
note = pitch + Optional(note_length | broken_rhythm).setDebug()

rest = Literal("z") | Literal("x")
multi_rest = Literal("Z")

element = pitch | rest | White(ws=" \t")

enumerated_repeat = "[" + digits
bar_indicator = (Literal("|") + Optional(Literal("]") | Literal(":") | Literal("|"))) | Literal("[|") | Literal(":|") | Literal("::") | enumerated_repeat | Literal("|")

bar = bar_indicator.setName('bar indicator') + OneOrMore(element) + bar_indicator

line = OneOrMore(bar)

abc_music = OneOrMore(line)

notes = Word("abcdefgABCDEFG,'^_=0123456789/zZx()[]|:~ {}")
abc_tune = abc_header + OneOrMore(notes).setResultsName("body")

def parse_string(s):
    result = abc_tune.parseString(s)
    return result

