from enum import Enum, unique


@unique
class Opt(Enum):
    Tool = "tool"
    Username = "-u"
    Caption = "-c"
    RecentPostLimit = "-rpl"
    File = "-file"
