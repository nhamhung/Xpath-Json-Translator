class XpathPathError(Exception):
    pass

class XpathLexerError(XpathPathError):
    pass

class XpathParserError(XpathPathError):
    pass