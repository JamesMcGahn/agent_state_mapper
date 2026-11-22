from enum import StrEnum


class MAPPING_SOURCE(StrEnum):
    CALL_ANALYSIS = "Call Analysis Provider"
    KEYWORD_MATCH = "Keyword Match"
    AUX_MATCH = "Aux Match"
    NO_SOURCE = "No Source"
