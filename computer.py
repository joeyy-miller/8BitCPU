import re

class EightBitComputer:
    def __init__(self):
        self.memory = [0] * 256  # 256 bytes of memory
        self.registers = {
            'A': 0,  # Accumulator
            'B': 0,  # General purpose register
            'SP': 0xFF,  # Stack Pointer
            'PC': 0  # Program Counter
        }
        self.flags = {
            'Z': 0,  # Zero flag
            'C': 0,  # Carry flag
            'N': 0   # Negative flag
        }
        self.interrupt_vector = 0x00  # Interrupt vector address
        self.interrupt_enabled = True
        self.halted = False
        self.io_buffer = ""
        self.display = [[0 for _ in range(16)] for _ in range(4)]  # 4x16 numeric display
        self.cursor_x = 0
        self.cursor_y = 0

    def load_program(self, program):
        for i, instruction in enumerate(program):
            self.memory[i] = instruction
        print(f"Program loaded: {self.memory[:len(program)]}")

    def fetch(self):
        instruction = self.memory[self.registers['PC']]
        self.registers['PC'] += 1
        print(f"Fetched instruction: {instruction:02X} at PC: {self.registers['PC']-1}")
        return instruction

    def execute(self, instruction):
        opcode = instruction >> 4
        operand = instruction & 0x0F
        print(f"Executing opcode: {opcode:X}, operand: {operand:X}")

        if opcode == 0x0:  # LOAD
            self.registers['A'] = self.memory[self.registers['PC']]
            self.registers['PC'] += 1
            print(f"LOAD: A = {self.registers['A']:02X}")
        elif opcode == 0x1:  # STORE
            self.memory[operand] = self.registers['A']
            print(f"STORE: memory[{operand:X}] = A = {self.registers['A']:02X}")
        elif opcode == 0x2:  # ADD
            self.registers['A'] += self.memory[operand]
            self.registers['A'] &= 0xFF  # Ensure 8-bit value
            print(f"ADD: A += memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x3:  # SUB
            self.registers['A'] -= self.memory[operand]
            self.registers['A'] &= 0xFF  # Ensure 8-bit value
            print(f"SUB: A -= memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0xF:
            if operand == 0x0:  # HALT
                self.halted = True
                print("HALT: Stopping execution")
            elif operand == 0x1:  # IN (New instruction for input)
                user_input = input("Enter a character: ")
                self.registers['A'] = ord(user_input[0]) if user_input else 0
                print(f"IN: User input '{user_input[0] if user_input else ''}' stored in A = {self.registers['A']:02X}")
            elif operand == 0x3:  # DISP (Display character at cursor)
                self.display[self.cursor_y][self.cursor_x] = self.registers['A']
                print(f"DISP: Displaying '{chr(self.registers['A'])}' at ({self.cursor_x}, {self.cursor_y})")
                self.cursor_x += 1
                if self.cursor_x >= 16:
                    self.cursor_x = 0
                    self.cursor_y = (self.cursor_y + 1) % 4
            elif operand == 0x4:  # CURS (Set cursor position)
                self.cursor_x = self.registers['A'] & 0x0F
                self.cursor_y = (self.registers['A'] >> 4) & 0x03
                print(f"CURS: Set cursor to ({self.cursor_x}, {self.cursor_y})")
            elif operand == 0x5:  # CLR (Clear display)
                self.display = [[0 for _ in range(16)] for _ in range(4)]
                self.cursor_x = 0
                self.cursor_y = 0
                print("CLR: Cleared display")

    def run(self):
        self.halted = False
        while not self.halted:
            instruction = self.fetch()
            self.execute(instruction)
        print("Program execution completed")

    def visualize(self):
        print("\n--- Computer State ---")
        print("Registers:", self.registers)
        print("Flags:", self.flags)
        print("Memory (first 16 bytes):", self.memory[:16])
        print("I/O Buffer:", self.io_buffer)
        print("Display:")
        for row in self.display:
            print(''.join(chr(c) if 32 <= c <= 126 else '.' for c in row))
        print("Cursor position: ({}, {})".format(self.cursor_x, self.cursor_y))
        print("---------------------")

class Assembler:
    def __init__(self):
        self.opcodes = {
            'LOAD': 0x0, 'STORE': 0x1, 'ADD': 0x2, 'SUB': 0x3,
            'HALT': 0xF0, 'IN': 0xF1, 'DISP': 0xF3, 'CURS': 0xF4, 'CLR': 0xF5
        }

    def assemble(self, code):
        program = []
        for line in code.split('\n'):
            line = re.split(r';', line)[0].strip()
            if not line:
                continue
            parts = re.split(r'[,\s]+', line)
            opcode = self.opcodes[parts[0]]
            if len(parts) > 1:
                operand = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                if opcode == 0x0:  # LOAD
                    program.append(opcode << 4)
                    program.append(operand)
                else:
                    program.append((opcode << 4) | (operand & 0x0F))
            else:
                program.append(opcode)
        print(f"Assembled program: {program}")
        return program

assembler = Assembler()

''' Hello World Program '''
display_demo = """
    CLR
    LOAD 0x48 ; Load 'H'
    DISP
    LOAD 0x45 ; Load 'E'
    DISP
    LOAD 0x4C ; Load 'L'
    DISP
    DISP
    LOAD 0x4F ; Load 'O'
    DISP
    LOAD 0x21 ; Load '!'
    DISP
    LOAD 0x10 ; Load cursor position (2nd row, 1st column)
    CURS
    LOAD 0x57 ; Load 'W'
    DISP
    LOAD 0x4F ; Load 'O'
    DISP
    LOAD 0x52 ; Load 'R'
    DISP
    LOAD 0x4C ; Load 'L'
    DISP
    LOAD 0x44 ; Load 'D'
    DISP
    HALT
"""

''' User Input Demo '''
input_demo = """
    CLR
    LOAD 0x45 ; Load 'E'
    DISP
    LOAD 0x6E ; Load 'n'
    DISP
    LOAD 0x74 ; Load 't'
    DISP
    LOAD 0x65 ; Load 'e'
    DISP
    LOAD 0x72 ; Load 'r'
    DISP
    LOAD 0x3A ; Load ':'
    DISP
    LOAD 0x20 ; Load ' '
    DISP
    IN       ; Get user input
    DISP     ; Display user input
    HALT
"""

program = assembler.assemble(display_demo)
computer = EightBitComputer()
computer.load_program(program)
computer.run()
computer.visualize()