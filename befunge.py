from random import choice
 
class Program:
    def __init__(self, source: str):
        self.width, self.grid = self._load(source)
        self.height = len(self.grid)

    def _load(self, source: str):#make a rectangular grid of characters from the source program
        rows = source.splitlines()
        max_width = max(len(row) for row in rows)
        ranks=[]
        for row in rows:
            ranks.append(row.ljust(max_width, " "))
        grid = [
            list(line.rstrip("\n"))
            for line in ranks
        ]
        return max_width, grid

    def get(self, x: int, y: int) -> str:
        return self.grid[y % self.height][x % self.width]

    def put(self, x: int, y: int, value: str):
        self.grid[y % self.height][x % self.width] = value
class Stack:
    def __init__(self):
        self._data = []

    def push(self, value: int):
        self._data.append(value)

    def pop(self) -> int:
        return self._data.pop() if self._data else 0

    def peek(self) -> int:
        return self._data[-1] if self._data else 0
class InstructionPointer:
    DIRECTIONS = {
        ">": (1, 0),
        "<": (-1, 0),
        "^": (0, -1),
        "v": (0, 1),
    }

    def __init__(self):#the instruction pointer (ip) has a POSITION and a DIRECTION 
        self.x = 0
        self.y = 0
        self.dx = 1
        self.dy = 0

    def move(self):#move one step in the current direction
        self.x += self.dx
        self.y += self.dy

    def set_direction(self, symbol: str):
        self.dx, self.dy = self.DIRECTIONS[symbol]

class InstructionSet:
    def __init__(self, interpreter):
        self.interpreter = interpreter#the source code, the stack and the instruction pointer 
        #of the ("parent") interpreter object are also available here now
        self.dispatch = {#this is a dictionary with function names as values
            "+": self.add,
            "-": self.sub,
            "*": self.mul,
            "/": self.div,
            "%": self.mod,
            "!": self.logical_not,
            "`": self.greater,
            ">": lambda: self.interpreter.ip.set_direction(">"),
            "<": lambda: self.interpreter.ip.set_direction("<"),
            "^": lambda: self.interpreter.ip.set_direction("^"),
            "v": lambda: self.interpreter.ip.set_direction("v"),
            "?": lambda: self.interpreter.ip.set_direction(choice(["^", "v", "<", ">"])),
            "_": self.horizontal_if,
            "|": self.vertical_if,
            "\"": self.string_mode,
            ":": self.duplicate,
            "\\": self.swap,
            "$": self.discard,
            ".": self.output_int, 
            ",": self.output_char,
            "#": self.trampoline,
            "p": self.put,
            "g": self.get,
            "@": self.stop,
            " ": lambda: None,  # do nothing 
        }

    def execute(self, instruction: str):
        if instruction.isdigit():
            self.interpreter.stack.push(int(instruction))
        elif instruction in self.dispatch:
            self.dispatch[instruction]()
        # anders: no-op

    def add(self):
        if len(self.interpreter.stack) < 2:
            return
        b = self.interpreter.stack.pop()
        a = self.interpreter.stack.pop()
        self.interpreter.stack.push(a + b)

    def sub(self):
        if len(self.interpreter.stack) < 2:
            return
        b = self.interpreter.stack.pop()
        a = self.interpreter.stack.pop()
        self.interpreter.stack.push(a - b)

    def mul(self):
        if len(self.interpreter.stack) < 2:
            return
        b = self.interpreter.stack.pop()
        a = self.interpreter.stack.pop()
        self.interpreter.stack.push(a * b)

    def div(self):
        if len(self.interpreter.stack) < 2:
            return
        a = self.interpreter.stack.pop()
        b = self.interpreter.stack.pop()
        self.interpreter.stack.push(0 if a == 0 else b // a)

    def mod(self):
        if len(self.interpreter.stack) < 2:
            return
        a = self.interpreter.stack.pop()
        b = self.interpreter.stack.pop()
        self.interpreter.stack.push(0 if a == 0 else b % a)

    def logical_not(self):
         if self.interpreter.stack:
            a = self.interpreter.stack.pop()
            self.interpreter.stack.push(0 if a != 0 else 1)

    def greater(self):
        if len(self.interpreter.stack) < 2:
            return
        a = self.interpreter.stack.pop()
        b = self.interpreter.stack.pop()
        self.interpreter.stack.push(1 if b > a else 0)

    def horizontal_if(self):
        if not self.interpreter.stack:
            return
        a = self.interpreter.stack.pop()
        self.interpreter.ip.set_direction(">" if a == 0 else "<")

    def vertical_if(self):
        if self.interpreter.stack.isEmpty():
            return
        a = self.interpreter.stack.pop()
        self.interpreter.ip.set_direction("v" if a == 0 else "^")

    def string_mode(self):
        self.interpreter.ip.move()  # skip the opening quote
        while True:
            instruction = self.interpreter.program.get(self.interpreter.ip.x, self.interpreter.ip.y)
            if instruction == "\"":
                break
            self.interpreter.stack.push(ord(instruction))
            self.interpreter.ip.move()  

    def duplicate(self):
        try:  
            a = self.interpreter.stack.peek()
            self.interpreter.stack.push(a)
        except IndexError:
            self.interpreter.stack.push(0)

    def swap(self):
        if not self.interpreter.stack:
            return
        else:
            a = self.interpreter.stack.pop()
            try:  
                b = self.interpreter.stack.pop()
            except IndexError:
                b = 0
        self.interpreter.stack.push(a)
        self.interpreter.stack.push(b)

    def discard(self):
        if self.interpreter.stack:
            self.interpreter.stack.pop()

    def output_int(self):
        if self.interpreter.stack:
            a = self.interpreter.stack.pop()
            print(a, end=' ')  

    def output_char(self):
        if self.interpreter.stack():
            a = self.interpreter.stack.pop()
            print(chr(a), end='')

    def trampoline(self):
        self.interpreter.ip.move()  # skip the next cell

    def put(self):  
        if len(self.interpreter.stack) < 3:
            return
        y = self.interpreter.stack.pop()
        x = self.interpreter.stack.pop()    
        v = self.interpreter.stack.pop()
        self.interpreter.program.put(x, y, chr(v % 256))  # wrap to 0-255

    def get(self):
        if len(self.interpreter.stack) < 2:
            return  
        y = self.interpreter.stack.pop()
        x = self.interpreter.stack.pop()
        value = self.interpreter.program.get(x, y)
        self.interpreter.stack.push(ord(value))  # push ASCII value 

    def stop(self):
        self.interpreter.running = False

class Interpreter:
    def __init__(self, source: str):
        self.program = Program(source)
        self.stack = Stack()
        self.ip = InstructionPointer()
        self.instructions = InstructionSet(self)#the interpreter object itself is passed, 
        #so its stack and instruction pointer can be changed
        self.running = True

    def step(self):
        instruction = self.program.get(self.ip.x, self.ip.y)
        self.instructions.execute(instruction)
        self.ip.move()

    def run(self):
        while self.running:#the program can be stopped by setting self.running to False 
              self.step()

def interpret(source: str):
    interpreter = Interpreter(source)
    interpreter.run()
