import tkinter as tk
from tkinter import ttk
import time
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
        self.interrupt_vector = 0xFE  # Interrupt vector address
        self.interrupt_enabled = True
        self.halted = False
        self.io_buffer = ""
        self.text_display = [[0 for _ in range(16)] for _ in range(4)]  # 4x16 character display
        self.graphics_display = [[0 for _ in range(32)] for _ in range(32)]  # 32x32 pixel display
        self.display_mode = 'text'  # 'text' or 'graphics'
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_offset = 0
        self.debug = True  # Set to False to disable debug prints
        self.delay = 0.1 # ability to slow down the computer

    def load_program(self, program):
        for i, instruction in enumerate(program):
            if i < len(self.memory):
                self.memory[i] = instruction
            else:
                print(f"Warning: Program too large for memory. Truncated at byte {i}.")
                break
        print(f"Loaded {min(len(program), len(self.memory))} bytes into memory.")

    def fetch(self):
        if self.registers['PC'] < len(self.memory):
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
        elif opcode == 0xA:  # JMP
            self.registers['PC'] = (self.memory[self.registers['PC']] << 4) | operand
            if self.debug:
                print(f"JMP: PC = {self.registers['PC']:02X}")
        elif opcode == 0xB:  # JZ
            if self.flags['Z']:
                self.registers['PC'] = (self.memory[self.registers['PC']] << 4) | operand
                if self.debug:
                    print(f"JZ: Zero flag set, jumping to {self.registers['PC']:02X}")
            else:
                self.registers['PC'] += 1
                if self.debug:
                    print("JZ: Zero flag not set, not jumping")
        elif opcode == 0xC:  # JNZ
            if not self.flags['Z']:
                self.registers['PC'] = (self.memory[self.registers['PC']] << 4) | operand
                if self.debug:
                    print(f"JNZ: Zero flag not set, jumping to {self.registers['PC']:02X}")
            else:
                self.registers['PC'] += 1
                if self.debug:
                    print("JNZ: Zero flag set, not jumping")
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
            if instruction_count > 248000: # 248k max instructions
                print("Execution limit reached. Halting.")
                break
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
                    if opcode in [0xA, 0xB, 0xC, 0xD]:  # Jump and call instructions
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

class VisualEmulator:
    def __init__(self, computer):
        self.computer = computer
        self.root = tk.Tk()
        self.root.title("8-bit Computer Emulator")
        self.root.geometry("800x700")  # Increased height for status display

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Text Display
        text_frame = ttk.LabelFrame(main_frame, text="Text Display", padding="5")
        text_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.text_display = tk.Text(text_frame, height=4, width=16, font=('Courier', 14))
        self.text_display.pack(expand=True, fill=tk.BOTH)

        # Graphics Display
        graphics_frame = ttk.LabelFrame(main_frame, text="Graphics Display", padding="5")
        graphics_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.graphics_display = tk.Canvas(graphics_frame, width=320, height=320, bg='white')
        self.graphics_display.pack(expand=True, fill=tk.BOTH)

        # Registers
        reg_frame = ttk.LabelFrame(main_frame, text="Registers", padding="5")
        reg_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.reg_vars = {}
        for i, reg in enumerate(['A', 'B', 'SP', 'PC']):
            ttk.Label(reg_frame, text=f"{reg}:").grid(row=i, column=0, padx=5, pady=2)
            self.reg_vars[reg] = tk.StringVar()
            ttk.Entry(reg_frame, textvariable=self.reg_vars[reg], width=5, state='readonly').grid(row=i, column=1, padx=5, pady=2)

        # Flags
        flag_frame = ttk.LabelFrame(main_frame, text="Flags", padding="5")
        flag_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.flag_vars = {}
        for i, flag in enumerate(['Z', 'C', 'N']):
            ttk.Label(flag_frame, text=f"{flag}:").grid(row=i, column=0, padx=5, pady=2)
            self.flag_vars[flag] = tk.StringVar()
            ttk.Entry(flag_frame, textvariable=self.flag_vars[flag], width=5, state='readonly').grid(row=i, column=1, padx=5, pady=2)

        # Memory Viewer
        mem_frame = ttk.LabelFrame(main_frame, text="Memory", padding="5")
        mem_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.memory_display = tk.Text(mem_frame, height=10, width=50, font=('Courier', 10))
        self.memory_display.pack(expand=True, fill=tk.BOTH)

        # Status Display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.status_display = tk.Text(status_frame, height=3, width=50, font=('Courier', 10))
        self.status_display.pack(expand=True, fill=tk.BOTH)

        # Control Buttons
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Button(control_frame, text="Step", command=self.step).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Run", command=self.run).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Quit", command=self.quit).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        for i in range(5):
            main_frame.rowconfigure(i, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def update_display(self):
        # Update Text Display
        self.text_display.delete('1.0', tk.END)
        for row in self.computer.text_display:
            self.text_display.insert(tk.END, ''.join([chr(c) if 32 <= c <= 126 else '.' for c in row]) + '\n')

        # Update Graphics Display
        self.graphics_display.delete("all")
        for y, row in enumerate(self.computer.graphics_display):
            for x, pixel in enumerate(row):
                if pixel:
                    self.graphics_display.create_rectangle(x*10, y*10, (x+1)*10, (y+1)*10, fill="black")

        # Update Registers
        for reg, var in self.reg_vars.items():
            var.set(f"{self.computer.registers[reg]:02X}")

        # Update Flags
        for flag, var in self.flag_vars.items():
            var.set(f"{self.computer.flags[flag]}")

        # Update Memory Display
        self.memory_display.delete('1.0', tk.END)
        for i in range(0, 256, 16):
            line = f"{i:02X}: " + " ".join([f"{self.computer.memory[i+j]:02X}" for j in range(16)]) + "\n"
            self.memory_display.insert(tk.END, line)

        # Update Status Display
        self.status_display.delete('1.0', tk.END)
        self.status_display.insert(tk.END, f"PC: {self.computer.registers['PC']:02X}\n")
        self.status_display.insert(tk.END, f"Last Instruction: {self.computer.last_instruction:02X}\n")
        self.status_display.insert(tk.END, f"Halted: {self.computer.halted}")

        self.root.after(100, self.update_display)

    def step(self):
        if not self.computer.halted:
            instruction = self.computer.fetch()
            self.computer.execute(instruction)
            self.computer.last_instruction = instruction
            self.update_display()
            self.root.update()

    def run(self):
        self.computer.running = True
        while self.computer.running and not self.computer.halted:
            self.step()
            time.sleep(0.1)  # Slow down execution to 10 steps per second
            self.root.update()

    def stop(self):
        self.computer.running = False

    def reset(self):
        self.computer.__init__()
        self.computer.load_program(program)  # Reload the program
        self.computer.last_instruction = 0
        self.update_display()

    def quit(self):
        self.root.quit()

    def start(self):
        self.root.mainloop()

# The rest of the code (EightBitComputer and Assembler classes) remains unchanged

# Example usage
if __name__ == "__main__":
    assembler = Assembler()
    
    animation_program = """
    ; Initialize variables
LOAD 0x10  ; X position
STORE 0    ; Store in memory address 0
LOAD 0x10  ; Y position
STORE 1    ; Store in memory address 1
LOAD 0x01  ; X direction (1 or -1)
STORE 2
LOAD 0x01  ; Y direction (1 or -1)
STORE 3

; Switch to graphics mode
LOAD 0x01
GMODE

; Main loop
MAIN_LOOP:
    ; Clear previous dot
    LOAD 0   ; Load X
    STORE 4  ; Temporary storage
    LOAD 1   ; Load Y
    SHL      ; Shift left 5 times to multiply by 32
    SHL
    SHL
    SHL
    SHL
    ADD 4    ; Add X to get pixel position
    LOAD 0x00  ; Set pixel to 0 (off)
    GPIX

    ; Update X position
    LOAD 0   ; Load X
    ADD 2    ; Add X direction
    STORE 0  ; Store new X

    ; Check X bounds
    SUB 0x1F  ; Subtract 31
    JZ BOUNCE_X  ; If result is 0, we've hit the right edge
    ADD 0x1F  ; Add 31 back
    JZ BOUNCE_X  ; If result is 0, we've hit the left edge
    JMP UPDATE_Y  ; If not, continue to Y update

BOUNCE_X:
    LOAD 2   ; Load X direction
    NOT      ; Flip all bits
    ADD 1    ; Add 1 to get two's complement (reverses direction)
    STORE 2  ; Store new X direction
    JMP UPDATE_Y

UPDATE_Y:
    ; Update Y position
    LOAD 1   ; Load Y
    ADD 3    ; Add Y direction
    STORE 1  ; Store new Y

    ; Check Y bounds
    SUB 0x1F  ; Subtract 31
    JZ BOUNCE_Y  ; If result is 0, we've hit the bottom edge
    ADD 0x1F  ; Add 31 back
    JZ BOUNCE_Y  ; If result is 0, we've hit the top edge
    JMP DRAW_DOT  ; If not, continue to draw dot

BOUNCE_Y:
    LOAD 3   ; Load Y direction
    NOT      ; Flip all bits
    ADD 1    ; Add 1 to get two's complement (reverses direction)
    STORE 3  ; Store new Y direction

DRAW_DOT:
    ; Draw new dot
    LOAD 0   ; Load X
    STORE 4  ; Temporary storage
    LOAD 1   ; Load Y
    SHL      ; Shift left 5 times to multiply by 32
    SHL
    SHL
    SHL
    SHL
    ADD 4    ; Add X to get pixel position
    LOAD 0x01  ; Set pixel to 1 (on)
    GPIX

    ; Delay loop
    LOAD 0xFF
DELAY:
    SUB 1
    JNZ DELAY

    JMP MAIN_LOOP  ; Repeat main loop
"""
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
    
    bouncing_dot_program = """
; Switch to graphics mode
LOAD 0x01
GMODE

; Draw a simple pattern
LOAD 0x00  ; Top-left corner
GPIX
LOAD 0x1F  ; Top-right corner
GPIX
LOAD 0x3E0  ; Bottom-left corner
GPIX
LOAD 0x3FF  ; Bottom-right corner
GPIX

; Draw a line
LOAD 0x00
LINE_LOOP:
    GPIX
    ADD 0x21  ; Move diagonally
    SUB 0x3FF
    JNZ LINE_LOOP

HALT
    """

    program = assembler.assemble(bouncing_dot_program)
    computer = EightBitComputer()
    computer.load_program(program)
    
    print("Running program...")
    for _ in range(1000):  # Run for 1000 instructions
        if computer.halted:
            break
        instruction = computer.fetch()
        computer.execute(instruction)
    
    print("Program execution completed or halted.")
    
    emulator = VisualEmulator(computer)
    emulator.run()