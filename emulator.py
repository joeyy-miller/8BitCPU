import tkinter as tk
from tkinter import ttk
import time
import re

from computer import EightBitComputer
from computer import Assembler

# Program
from program import program

class VisualEmulator:
    def __init__(self, computer):
        self.computer = computer
        self.root = tk.Tk()
        self.root.title("8-bit Computer Emulator")
        self.root.geometry("800x950")  # Increased height for status display
        self.running = False 
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

    def run(self):
        self.running = True
        while self.running:
            if not self.computer.halted:
                self.step()
            else:
                self.running = False
            self.root.update()
            time.sleep(0.01)  # Adjust this value to control animation speed

    def run(self):
        self.running = True
        while self.running and not self.computer.halted:
            self.step()
            time.sleep(0.1)  # Slow down execution to 10 steps per second
            self.root.update()

    def step(self):
        if not self.computer.halted:
            self.computer.run()
            self.update_display()
            
    def stop(self):
        self.running = False

    def reset(self):
        self.computer.__init__()
        self.computer.load_program(program)  # Reload the program
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

    running_program = assembler.assemble(program)
    
    emulator = VisualEmulator(computer)
    emulator.start()  # This will keep the window open
    
    
    computer = EightBitComputer()
    computer.load_program(running_program)
    
    
    
    print("Running program...")
    for _ in range(1000):  # Run for 1000 instructions
        if computer.halted:
            break
        instruction = computer.fetch()
        computer.execute(instruction)
    
    print("Program execution completed or halted.")