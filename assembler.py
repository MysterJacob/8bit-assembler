from more_itertools import peekable

class SyntaxError(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
class UnexpectedEOF(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class pf:

    @staticmethod
    def consume2lf(s,line_number) -> int:
        while (char := next(s)) != "\n":pass
        return 1,None

    @staticmethod
    def is_comment(s):
        return s.peek() == "#"

    @staticmethod
    def parse_number(s):
        base = 10
        valid_literals = "1234567890xb"
        literal = []
        while s.peek() in valid_literals:
            char = next(s)
            literal.append(char)

            if len(literal) != 2:
                continue

            if literal[1] == "x":
                base = 16
            elif literal[1] == "b":
                base = 2

        return int("".join(literal),base)

    @staticmethod
    def consume_whs(s):
        while s.peek().isspace():
            next(s)

    @staticmethod
    def consume_opcode(s):
        opcode = ""
        while s.peek().isalpha():
            opcode += next(s)
        return opcode

    @staticmethod
    def parse_opcode(s,line_number):
        pf.consume_whs(s)
        opcode = pf.consume_opcode(s)
        pf.consume_whs(s)
        argument = None
        if s.peek() != ";":
            argument = pf.parse_number(s)

        pf.consume_whs(s)

        if next(s) != ";":
            raise SyntaxError(f"Syntax error at line {self._line}")

        return 1,("o",opcode,argument)

class Parser:
    def __init__(self,file_path : str):

        stream = open(file_path,"r")
        content = stream.read()
        stream.close()
        self.raw_data = peekable(content)

        self.parse_tree = {
            pf.is_comment : pf.consume2lf,
            lambda _: True : pf.parse_opcode
        }
        self._line = 1
        self.result = []

    def _use_parser(self,parser):
        lines_parsed,result = parser(self.raw_data,self._line)
        if result != None:
            self.result.append( (self._line,*result) )

        self._line += lines_parsed

    def check_parser(self,check,parser):
        if check(self.raw_data):
            self._use_parser(parser)
            return True
        return False

    def _is_eof(self):
        try:
            pf.consume_whs(self.raw_data)
            return False
        except StopIteration:
            return True

    def _single_parse(self):
        for check,parser in self.parse_tree.items():
            if self.check_parser(check,parser):
                return
        raise SyntaxError(f"Syntax error at line {self._line}")

    def parse(self):
        while not self._is_eof():
            try:
                self._single_parse()
            except StopIteration:
                raise UnexpectedEOF(f"Unexpected EOF at {self._line}")
        return self.result

if __name__ == "__main__":
    p = Parser("program.ebt")
    print(p.parse())
