"""Implementation of ATermDecoder

hacked from JSONDecoder code
"""
import re

__all__ = ['ATerm','decode']

DEBUG=False


FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

def debug(msg):
    if DEBUG:
        print "DEBUG:",msg


def linecol(doc, pos):
    lineno = doc.count('\n', 0, pos) + 1
    if lineno == 1:
        colno = pos
    else:
        colno = pos - doc.rindex('\n', 0, pos)
    return lineno, colno

def errmsg(msg, doc, pos, end=None):
    # Note that this function is called from _speedups
    lineno, colno = linecol(doc, pos)
    if end is None:
        #fmt = '{0}: line {1} column {2} (char {3})'
        #return fmt.format(msg, lineno, colno, pos)
        fmt = '%s: line %d column %d (char %d)'
        return fmt % (msg, lineno, colno, pos)
    endlineno, endcolno = linecol(doc, end)
    #fmt = '{0}: line {1} column {2} - line {3} column {4} (char {5} - {6})'
    #return fmt.format(msg, lineno, colno, endlineno, endcolno, pos, end)
    fmt = '%s: line %d column %d - line %d column %d (char %d - %d)'
    return fmt % (msg, lineno, colno, endlineno, endcolno, pos, end)


STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
BACKSLASH = {
    '"': u'"', '\\': u'\\', '/': u'/',
    'b': u'\b', 'f': u'\f', 'n': u'\n', 'r': u'\r', 't': u'\t',
}

DEFAULT_ENCODING = "utf-8"

def scanstring(s, end, encoding=None, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match):
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.
    
    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    if encoding is None:
        encoding = DEFAULT_ENCODING
    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise ValueError(
                errmsg("Unterminated string starting at", s, begin))
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            if not isinstance(content, unicode):
                content = unicode(content, encoding)
            _append(content)
        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = "Invalid control character %r at" % (terminator,)
                #msg = "Invalid control character {0!r} at".format(terminator)
                raise ValueError(errmsg(msg, s, end))
            else:
                _append(terminator)
                continue
        try:
            esc = s[end]
        except IndexError:
            raise ValueError(
                errmsg("Unterminated string starting at", s, begin))
        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = "Invalid \\escape: " + repr(esc)
                raise ValueError(errmsg(msg, s, end))
            end += 1
        else:
            # Unicode escape sequence
            esc = s[end + 1:end + 5]
            next_end = end + 5
            if len(esc) != 4:
                msg = "Invalid \\uXXXX escape"
                raise ValueError(errmsg(msg, s, end))
            uni = int(esc, 16)
            # Check for surrogate pair on UCS-4 systems
            if 0xd800 <= uni <= 0xdbff and sys.maxunicode > 65535:
                msg = "Invalid \\uXXXX\\uXXXX surrogate pair"
                if not s[end + 5:end + 7] == '\\u':
                    raise ValueError(errmsg(msg, s, end))
                esc2 = s[end + 7:end + 11]
                if len(esc2) != 4:
                    raise ValueError(errmsg(msg, s, end))
                uni2 = int(esc2, 16)
                uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                next_end += 6
            char = unichr(uni)
            end = next_end
        # Append the unescaped character
        _append(char)
    return u''.join(chunks), end

match_whitespace = re.compile(r'[ \t\n\r]*', FLAGS).match
WHITESPACE = ' \t\n\r'

ID_START = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
match_ID = re.compile(r'[A-Z]+[A-Za-z0-9]*', FLAGS).match

NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))
match_number = NUMBER_RE.match

ID_RE = re.compile(
    r'([A-Za-z]+[0-9_A-Za-z]*)',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))

encoding = 'utf-8'
strict = True

class ATerm (object):
    def __init__(self,id,params=[]):
        self.id = id
        self.params = params
        
    def __repr__(self):
        if len(self.params) >0:
            return "%s(%s)" % (self.id,repr(self.params)[1:-1])
        return "%s" % self.id

def expect(string,idx,s):
    idx = skip_whitespace(string,idx)
    if not string[idx:idx+len(s)] == s:
        raise ValueError( errmsg("Expecting "+s, string, idx))
    else:
        return idx+len(s)

def skip_whitespace(string,idx):
    if idx<len(string) and string[idx] in WHITESPACE:
        m = match_whitespace(string,idx)
        debug("skip whitespace %i" % (m.end()) )
        return m.end()
    return idx

def scan(string, idx):
        
    idx = skip_whitespace(string,idx)
   
    nextchar = string[idx:idx+1]
     
    if nextchar == None:
        return None
    if nextchar == '"':
        return scanstring(string, idx + 1, encoding, strict)
    elif nextchar == '[':
        l,idx = parse_list( string, idx + 1,']' )
        return ( l, idx )
            
    m = match_number(string, idx)
    if m is not None:
        integer, frac, exp = m.groups()
        if frac or exp:
            res = float(integer + (frac or '') + (exp or ''))
        else:
            res = int(integer)
        return res, m.end()
        
    m = match_ID(string,idx)
    if m is not None:
        id_ = string[ m.start() : m.end() ]
        idx = m.end()
        if string[idx:idx+1] != '(':
           return ( ATerm(id_), m.end() )
        idx = expect(string,idx,'(')
        params,idx = parse_list(string,idx,')')
        return ATerm(id_,params),idx
                
    raise ValueError( errmsg("Syntax error", string, idx))

def parse_list(string,idx,terminator):
    l = []
    debug("parse list "+string[idx:idx+20])
    
    while True:
        idx = skip_whitespace(string,idx)
        if string[idx] == terminator:
            idx +=1
            break

        val,idx = scan(string,idx)
        debug("append "+repr(val))
        debug("now at "+string[idx:idx+20])
        l.append( val )
        idx = skip_whitespace(string,idx)
        
        nextchar = string[idx:idx+1]
                
        if nextchar is None:
            raise ValueError( errmsg("EOF in list, at least %s expected" % terminator, string, idx))
        if nextchar == ',':
            idx += 1 
            continue
        elif nextchar == terminator:
            idx += 1
            break
        else:
            raise ValueError( errmsg("Syntax error while parsing list", string, idx))
    
    return l,idx

def decode(string):
    res,idx = scan(string,0)
    return res

if __name__ == '__main__':
    import sys
    
    print decode ( sys.stdin.read())
    
    


