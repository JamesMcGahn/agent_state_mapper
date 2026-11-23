from enum import StrEnum


class MAPPING_SOURCE(StrEnum):
    CALL_ANALYSIS = "Call Analysis Provider"
    COMMON_KEYWORD_MATCH = "Keyword Match"
    COMMON_AUX_MATCH = "Aux Match"
    PROVIDER_STATE_AUX_MATCH = "Provider State Aux Match"
    PROVIDER_BASE_STATE = "Provider Base State Match"
    NO_SOURCE = "No Source"
