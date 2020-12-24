from TemporalParser.building_blocks.call.call import FuncCall, MethodCall, Call
from TemporalParser.building_blocks.time_connector.time_connector import TimeConnector
from TemporalParser.condition.condition import Condition
from TemporalParser.event.event import *
from TemporalParser.phrase.phrase import Phrase, SimplePhrase, ComplexPhrase

building_blocks_classes = [
    TimeConnector,
    Phrase,
    SimplePhrase,
    ComplexPhrase,
    Call,
    FuncCall,
    MethodCall,
    Event,
    Condition
]

building_blocks = {

}

for c in building_blocks_classes:
    building_blocks[c.__name__] = c
