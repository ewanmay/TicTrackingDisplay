from enum import Enum
class State(Enum): 
    Start = 1,
    Playing = 2,
    Paused = 3

class LogMethod(Enum):
    Serial = 1,
    File = 2,
    Db = 3