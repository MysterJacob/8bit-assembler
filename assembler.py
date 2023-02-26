#!/bin/env python3
from more_itertools import peekable
from opcodes import opcodes

class SyntaxError(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class UndefinedSection(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class UnexpectedEOF(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class pf:
    @staticmethod
    def is_comment(s):
        return s.peek() == "#"

    @staticmethod
    def is_label(s):
        return s.peek() == "."

    @staticmethod
    def is_assembler_instruction(s):
        return s.peek() == "%"

    @staticmethod
    def consume2lf(s,line_number) -> int:
        while (char := next(s)) != "\n":pass
        return 1,None

    @staticmethod
    def consume_label_argument(s):
        valid_literals = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy_"
        literal = ""
        while s.peek() in valid_literals:
            char = next(s)
            literal += char
        return literal

    @staticmethod
    def consume_argument(s):
        if s.peek().isnumeric():
            return pf.consume_number(s)
        else:
            label = pf.consume_label_argument(s)
            return label

    @staticmethod
    def consume_label(s,line_number):
        valid_literals = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
        label = ""
        next(s)
        while s.peek() in valid_literals:
            label += next(s)
        if next(s) != ":":
            raise SyntaxError(f"Not valid label at line {line_number}")
        return ("l",label)

    @staticmethod
    def consume_assembler_instruction(s,line_number):
        valid_literals = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy_"
        instruction = ""
        next(s)
        while s.peek() in valid_literals:
            instruction += next(s)
        pf.consume_whs(s)
        argument = pf.consume_argument(s)
        return (instruction,argument)

    @staticmethod
    def consume_number(s):
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
        new_line = False
        while s.peek().isspace():
            if next(s) == "\n":
                new_line = True
        return new_line

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
            argument = pf.consume_argument(s)

        if next(s) != ";":
            raise SyntaxError(f"Syntax error at line {line_number}")

        return ("o",opcode,argument)

class Parser:
    def __init__(self,file_path : str):

        self.stream = open(file_path,"r")
        self.raw_data = peekable(self._stream_iterator(self.stream))

        self.parse_tree = {
            pf.is_comment : pf.consume2lf,
            pf.is_label : pf.consume_label,
            pf.is_assembler_instruction : self.assembler_instruction,
            lambda _: True : pf.parse_opcode
        }

        self._line = 1
        self.opcode_index = 0
        self.result = []
        self.labels = {}
        self.main_label = "start"
        self.base = 0

    def _stream_iterator(self,stream):
        for line in stream:
            yield from iter(line)
        yield "\n"
        stream.close()

    def _use_parser(self,parser):
        result = parser(self.raw_data,self._line)
        if result == None: return


        self.result.append( (self._line,self.opcode_index,*result) )
        if result[0] == "l":
            if result[1] in self.labels:
                raise SyntaxError(f"Second declaration of label {result[1]} at line {self._line}")
            self.labels[result[1]] =\
                (self._line,self.opcode_index,*result)
        else:
            self.opcode_index += 1

    def assembler_instruction(self,s,line_number):
        instruction,argument = pf.consume_assembler_instruction(s,line_number)
        if instruction == "base":
            self.base = argument
        elif instruction == "main_label":
            self.main_label = argument
        else:
            raise SyntaxError(f"Unknown assembler instruction at line {line_number}")
        return None

    def check_parser(self,check,parser):
        if check(self.raw_data):
            self._use_parser(parser)
            return True
        return False

    def _is_eof(self):
        try:
            if pf.consume_whs(self.raw_data):
                self._line += 1
            return False
        except Exception:
            return True

    def _single_parse(self):
        for check,parser in self.parse_tree.items():
            if self.check_parser(check,parser):
                return
        raise SyntaxError(f"Syntax error at line {self._line}")

    def _replace_labels(self,part : tuple):
        if part[2] != "o": return part
        if type(part[-1]) != str: return part
        label = self.labels.get(part[-1],None)
        if label == None:
            raise SyntaxError(f"Unknow label at line {part[0]}")
        return (*part[:-1],label[1])

    def _second_phase(self):
        if not self.main_label in self.labels:
            raise UnknownSection(f"No main_label named {label}")

        self.result = list(
            map(
                lambda p : self._replace_labels(p),
                self.result
            )
        )

    def parse(self):
        while not self._is_eof():
            try:
                self._single_parse()
            except Exception as e:
                self.stream.close()
                if isinstance(e,StopIteration):
                    raise UnexpectedEOF(f"Unexpected EOF at {self._line}")
                else:
                    raise e

        self._second_phase()
        return self.result, self.labels, self.main_label, self.base

class Assembler:
    def write_op(self,data : tuple,stream):
        line,index,type,*info = data
        if type != "o": return
        opcode,argument = info
        has_argument,opcode_value = opcodes.get(opcode,(None,None))

        if opcode_value == None:
            raise SyntaxError(f"Unknown opcode {opcode} at line {line}")

        if has_argument and argument == None:
            raise SyntaxError(f"Opcode {opcode} at line {line} requires an argument")
        elif not has_argument and argument != None:
            raise SyntaxError(f"Opcode {opcode} at line {line} can't have an argument")
        elif argument == None:
            argument = 0
        elif argument > 255:
            raise SyntaxError(f"Argument of opcode {opcode} at line {line} must be one byte (0-255)")

        stream.seek(index*2)
        stream.write(bytes([argument,opcode_value]))

    def calculate_base_label(self,parsed,labels : dict,main_label : str):
        label = labels.get(main_label)
        line,index,type,name = label
        start = index
        stop = len(parsed)-1
        for i,next_parsed in enumerate(parsed[line:]):
            if  next_parsed[2] == "l":
                stop = start + i 
                break
        size = stop-start
        return start,stop,size
    #TODO
    def move2base_label(self,parsed : list,labels : dict,main_label : str):
        start,stop,size = self.calculate_base_label(parsed,labels,main_label)
        print(start,stop,size)
        new_base_label_index = 0
        for i,data in enumerate(parsed[:stop+1]):
            line,index,type,*info = data
            if index >= start and index < stop:
                parsed[i] = (line,new_base_label_index,type,*info)
                if type != "l":
                    new_base_label_index += 1
            else:
                parsed[i] = (line,index+size,type,*info)

    def assemble(self,input_file_path : str,output_file_path : str):
        p = Parser(input_file_path)
        output_stream = open(output_file_path,"wb+")
        parsed, labels, main_label, base_offset = p.parse()
        print(parsed)
        self.move2base_label(parsed,labels,main_label)
        print(parsed)
        try:
            for data in parsed:
                self.write_op(data,output_stream)
        except Exception as e:
            raise e
        finally:
            output_stream.close()

if __name__ == "__main__":
    a = Assembler()
    a.assemble("program.ebt","program.bin")
