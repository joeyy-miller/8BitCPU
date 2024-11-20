import re
import time

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
        self.interrupt_vector = 0xFE  # Interrupt vector address
        self.interrupt_enabled = True
        self.last_instruction = 0
        self.halted = False
        self.io_buffer = ""
        self.text_display = [[0 for _ in range(16)] for _ in range(4)]  # 4x16 character display
        self.graphics_display = [[0 for _ in range(32)] for _ in range(32)]  # 32x32 pixel display
        self.display_mode = 'text'  # 'text' or 'graphics'
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_offset = 0
        self.memory_size = 256 # define memory size
        self.debug = True  # Set to False to disable debug prints
        self.delay = 0 # ability to slow down the computer

    def load_program(self, program):
        for i, instruction in enumerate(program):
            if i < len(self.memory):
                self.memory[i] = instruction
            else:
                print(f"Warning: Program too large for memory. Truncated at byte {i}.")
                break
        print(f"Loaded {min(len(program), len(self.memory))} bytes into memory.")
        
    def fetch(self):
        if self.registers['PC'] < self.memory_size:
            instruction = self.memory[self.registers['PC']]
            self.registers['PC'] += 1
            if self.debug:
                print(f"Fetched instruction: {instruction:02X} at PC: {self.registers['PC']-1}")
            return instruction
        else:
            self.halted = True
            print("Program counter out of memory range. Halting.")
            return 0xF0  # HALT instruction

    def push(self, value):
        if self.registers['SP'] > 0:
            self.registers['SP'] -= 1
            self.memory[self.registers['SP']] = value
            if self.debug:
                print(f"Pushed {value:02X} to stack at SP: {self.registers['SP']:02X}")
        else:
            print("Stack overflow. Halting.")
            self.halted = True

    def pop(self):
        if self.registers['SP'] < 0xFF:
            value = self.memory[self.registers['SP']]
            self.registers['SP'] += 1
            if self.debug:
                print(f"Popped {value:02X} from stack at SP: {self.registers['SP']-1:02X}")
            return value
        else:
            print("Stack underflow. Halting.")
            self.halted = True
            return 0

    def execute(self, instruction):
        self.last_instruction = instruction
        opcode = instruction >> 4
        operand = instruction & 0x0F
        if self.debug:
            print(f"Executing opcode: {opcode:X}, operand: {operand:X}")

        if opcode == 0x0:  # LOAD
            self.registers['A'] = self.memory[self.registers['PC']]
            self.registers['PC'] += 1
            if self.debug:
                print(f"LOAD: A = {self.registers['A']:02X}")
        elif opcode == 0x1:  # STORE
            self.memory[operand] = self.registers['A']
            if self.debug:
                print(f"STORE: memory[{operand:X}] = A = {self.registers['A']:02X}")
        elif opcode == 0x2:  # ADD
            self.registers['A'] += self.memory[operand]
            self.registers['A'] &= 0xFF  # Ensure 8-bit value
            if self.debug:
                print(f"ADD: A += memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x3:  # SUB
            self.registers['A'] -= self.memory[operand]
            self.registers['A'] &= 0xFF  # Ensure 8-bit value
            if self.debug:
                print(f"SUB: A -= memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x4:  # AND
            self.registers['A'] &= self.memory[operand]
            if self.debug:
                print(f"AND: A &= memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x5:  # OR
            self.registers['A'] |= self.memory[operand]
            if self.debug:
                print(f"OR: A |= memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x6:  # XOR
            self.registers['A'] ^= self.memory[operand]
            if self.debug:
                print(f"XOR: A ^= memory[{operand:X}], A = {self.registers['A']:02X}")
        elif opcode == 0x7:  # NOT
            self.registers['A'] = ~self.registers['A'] & 0xFF
            if self.debug:
                print(f"NOT: A = ~A, A = {self.registers['A']:02X}")
        elif opcode == 0x8:  # SHL
            self.flags['C'] = (self.registers['A'] & 0x80) >> 7
            self.registers['A'] = (self.registers['A'] << 1) & 0xFF
            if self.debug:
                print(f"SHL: A << 1, A = {self.registers['A']:02X}, C = {self.flags['C']}")
        elif opcode == 0x9:  # SHR
            self.flags['C'] = self.registers['A'] & 0x01
            self.registers['A'] = (self.registers['A'] >> 1) & 0xFF
            if self.debug:
                print(f"SHR: A >> 1, A = {self.registers['A']:02X}, C = {self.flags['C']}")
        elif opcode == 0xA:  # JMP (relative)
            offset = self.memory[self.registers['PC']]
            self.registers['PC'] = (self.registers['PC'] + offset) % self.memory_size
        elif opcode == 0xB:  # JZ (relative)
            offset = self.memory[self.registers['PC']]
            if self.flags['Z']:
                self.registers['PC'] = (self.registers['PC'] + offset) % self.memory_size
            else:
                self.registers['PC'] += 1
        elif opcode == 0xC:  # JNZ (relative)
            offset = self.memory[self.registers['PC']]
            if not self.flags['Z']:
                self.registers['PC'] = (self.registers['PC'] + offset) % self.memory_size
            else:
                self.registers['PC'] += 1
        elif opcode == 0xD:  # CALL
            self.push((self.registers['PC'] + 1) & 0xFF)
            self.registers['PC'] = (self.memory[self.registers['PC']] << 4) | operand
            if self.debug:
                print(f"CALL: Pushed {(self.registers['PC']+1) & 0xFF:02X}, jumped to {self.registers['PC']:02X}")
        elif opcode == 0xE:  # RET
            self.registers['PC'] = self.pop()
            if self.debug:
                print(f"RET: PC = {self.registers['PC']:02X}")
        elif opcode == 0xF:
            if operand == 0x0:  # HALT
                self.halted = True
                if self.debug:
                    print("HALT: Stopping execution")
            elif operand == 0x1:  # IN
                self.registers['A'] = ord(input("Input: ")[0])
                if self.debug:
                    print(f"IN: A = {self.registers['A']:02X}")
            elif operand == 0x2:  # OUT
                print(chr(self.registers['A']), end='', flush=True)
                if self.debug:
                    print(f"OUT: Output '{chr(self.registers['A'])}'")
            elif operand == 0x3:  # DISP
                self.display_char(self.registers['A'])
                if self.debug:
                    print(f"DISP: Displaying '{chr(self.registers['A'])}' at ({self.cursor_x}, {self.cursor_y})")
            elif operand == 0x4:  # CURS
                self.cursor_x = self.registers['A'] & 0x0F
                self.cursor_y = (self.registers['A'] >> 4) & 0x03
                if self.debug:
                    print(f"CURS: Set cursor to ({self.cursor_x}, {self.cursor_y})")
            elif operand == 0x5:  # CLR
                self.clear_display()
                if self.debug:
                    print("CLR: Cleared display")
            elif operand == 0x6:  # GMODE
                self.display_mode = 'graphics' if self.registers['A'] else 'text'
                if self.debug:
                    print(f"GMODE: Set display mode to {self.display_mode}")
            elif operand == 0x7:  # GPIX
                x = self.registers['A'] & 0x1F
                y = (self.registers['A'] >> 5) & 0x1F
                self.set_pixel(x, y, 1)
                if self.debug:
                    print(f"GPIX: Set pixel at ({x}, {y})")
            elif operand == 0x8:  # SCROLL
                self.scroll_display(self.registers['A'])
                if self.debug:
                    print(f"SCROLL: Scrolled display by {self.registers['A']} lines")

        self.update_flags(self.registers['A'])

    def update_flags(self, value):
        self.flags['Z'] = 1 if value == 0 else 0
        self.flags['N'] = 1 if value & 0x80 else 0
        self.registers['A'] = value & 0xFF

    def display_char(self, char):
        if self.display_mode == 'text':
            self.text_display[self.cursor_y][self.cursor_x] = char
            self.cursor_x += 1
            if self.cursor_x >= 16:
                self.cursor_x = 0
                self.cursor_y = (self.cursor_y + 1) % 4

    def clear_display(self):
        if self.display_mode == 'text':
            self.text_display = [[0 for _ in range(16)] for _ in range(4)]
        else:
            self.graphics_display = [[0 for _ in range(32)] for _ in range(32)]
        self.cursor_x = 0
        self.cursor_y = 0

    def set_pixel(self, x, y, value):
        if 0 <= x < 32 and 0 <= y < 32:
            self.graphics_display[y][x] = value
            print(f"Set pixel at ({x}, {y}) to {value}")

    def scroll_display(self, lines):
        if self.display_mode == 'text':
            self.scroll_offset = (self.scroll_offset + lines) % 4

    def handle_interrupt(self):
        if self.interrupt_enabled:
            self.push(self.registers['PC'] & 0xFF)
            self.registers['PC'] = self.memory[self.interrupt_vector]
            if self.debug:
                print(f"Interrupt: Jumped to {self.registers['PC']:02X}")

    def run(self):
        self.halted = False
        instruction_count = 0
        while not self.halted:
            instruction = self.fetch()
            self.execute(instruction)
            instruction_count += 1
            time.sleep(self.delay)  # Add delay between instructions
            # Safety check to prevent infinite loops
            #if instruction_count > 248000: # 248k max instructions
            print("Execution limit reached. Halting.")
                #break
        print(f"Program halted after executing {instruction_count} instructions.")

class Assembler:
    def __init__(self):
        self.opcodes = {
            'LOAD': 0x0, 'STORE': 0x1, 'ADD': 0x2, 'SUB': 0x3,
            'AND': 0x4, 'OR': 0x5, 'XOR': 0x6, 'NOT': 0x7,
            'SHL': 0x8, 'SHR': 0x9, 'JMP': 0xA, 'JZ': 0xB,
            'JNZ': 0xC, 'CALL': 0xD, 'RET': 0xE,
            'HALT': 0xF0, 'IN': 0xF1, 'OUT': 0xF2, 'DISP': 0xF3,
            'CURS': 0xF4, 'CLR': 0xF5, 'GMODE': 0xF6, 'GPIX': 0xF7,
            'SCROLL': 0xF8
        }
        self.labels = {}
        self.macros = {}

    def assemble(self, code):
        # First pass: collect labels and macros
        lines = code.split('\n')
        program = []
        i = 0
        while i < len(lines):
            line = re.split(r';', lines[i])[0].strip()
            if not line:
                i += 1
                continue
            if line.startswith('%macro'):
                i = self.parse_macro(lines, i)
            elif ':' in line:
                label, _ = line.split(':', 1)
                self.labels[label.strip()] = len(program)
            else:
                program.append(line)
            i += 1

        # Second pass: assemble instructions
        assembled_program = []
        for line in program:
            parts = re.split(r'[,\s]+', line)
            if parts[0] in self.macros:
                assembled_program.extend(self.expand_macro(parts))
            else:
                opcode = self.opcodes[parts[0]]
                if len(parts) > 1:
                    if parts[1] in self.labels:
                        operand = self.labels[parts[1]]
                    else:
                        operand = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                    if opcode in [0xA, 0xB, 0xC]:  # Jump instructions (now relative)
                        assembled_program.append(opcode << 4)
                        # Calculate relative jump
                        jump_target = operand - (len(assembled_program) + 1)
                        assembled_program.append(jump_target & 0xFF)
                    elif opcode == 0xD:  # CALL instruction (still absolute)
                        assembled_program.append(opcode << 4 | (operand >> 8))
                        assembled_program.append(operand & 0xFF)
                    elif opcode == 0x0:  # LOAD
                        assembled_program.append(opcode << 4)
                        assembled_program.append(operand)
                    else:
                        assembled_program.append((opcode << 4) | (operand & 0x0F))
                else:
                    assembled_program.append(opcode)

        return assembled_program


    def parse_macro(self, lines, start_index):
        macro_def = lines[start_index].split()
        macro_name = macro_def[1]
        macro_args = macro_def[2:]
        macro_body = []
        i = start_index + 1
        while i < len(lines) and not lines[i].strip().startswith('%endmacro'):
            macro_body.append(lines[i].strip())
            i += 1
        self.macros[macro_name] = (macro_args, macro_body)
        return i + 1  # Skip the %endmacro line

    def expand_macro(self, macro_call):
        macro_name = macro_call[0]
        macro_args, macro_body = self.macros[macro_name]
        arg_values = macro_call[1:]
        expanded = []
        for line in macro_body:
            for arg, value in zip(macro_args, arg_values):
                line = line.replace(arg, value)
            expanded.append(line)
        return self.assemble('\n'.join(expanded))

# Example usage
assembler = Assembler()
example_program = """
%macro PRINT_HELLO 0
    LOAD 0x48 ; 'H'
    DISP
    LOAD 0x65 ; 'e'
    DISP
    LOAD 0x6C ; 'l'
    DISP
    LOAD 0x6C ; 'l'
    DISP
    LOAD 0x6F ; 'o'
    DISP
%endmacro

START:
    CLR
    PRINT_HELLO
    JMP GRAPHICS

GRAPHICS:
    LOAD 0x01
    GMODE
    LOAD 0x00 ; Set pixel at (0,0)
    GPIX
    LOAD 0x1F ; Set pixel at (31,0)
    GPIX
    LOAD 0x3E0 ; Set pixel at (0,31)
    GPIX
    LOAD 0x3FF ; Set pixel at (31,31)
    GPIX
    HALT
"""

program = assembler.assemble(example_program)
computer = EightBitComputer()
computer.load_program(program)
computer.run()

# After running, you can inspect the computer's state
print("Final register states:")
for reg, value in computer.registers.items():
    print(f"{reg}: {value:02X}")

print("\nFinal display state:")
for row in computer.text_display:
    print(''.join([chr(c) if 32 <= c <= 126 else '.' for c in row]))

print("\nGraphics display state (1 means pixel is set):")
for row in computer.graphics_display:
    print(''.join(['1' if pixel else '0' for pixel in row]))