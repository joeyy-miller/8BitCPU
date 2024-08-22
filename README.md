# 8-bit Computer Simulation

This project simulates a simple 8-bit computer with a basic instruction set, memory, registers, and a 4x16 character display. It includes an assembler to convert assembly language into machine code for the simulated computer.

## Features

- 256 bytes of memory
- 8-bit accumulator (A register)
- 4x16 character display
- Basic instruction set including arithmetic, memory operations, and I/O
- Assembler for converting assembly code to machine code
- User input capability

## Architecture

The simulated computer has the following components:

- Memory: 256 bytes
- Registers:
  - A: 8-bit accumulator
  - B: 8-bit general-purpose register (currently unused)
  - SP: 8-bit stack pointer
  - PC: 8-bit program counter
- Flags: Zero (Z), Carry (C), Negative (N)
- Display: 4 rows x 16 columns character display

## Instruction Set

The computer supports the following instructions:

- LOAD: Load a value into the accumulator
- STORE: Store the accumulator value in memory
- ADD: Add a memory value to the accumulator
- SUB: Subtract a memory value from the accumulator
- HALT: Stop program execution
- IN: Get user input
- DISP: Display the accumulator value on the screen
- CURS: Set the cursor position
- CLR: Clear the display

## Programming the Computer

To write programs for this computer, use the following assembly language format:

```
INSTRUCTION [OPERAND] ; Comment
```

Example:

```
LOAD 0x41 ; Load 'A' into the accumulator
DISP      ; Display 'A' on the screen
IN        ; Get user input
DISP      ; Display user input
HALT      ; Stop the program
```

### Instructions in Detail

1. LOAD: `LOAD 0xXX` or `LOAD XX`
   Loads an 8-bit value into the accumulator.

2. STORE: `STORE X`
   Stores the accumulator value in memory address X (0-15).

3. ADD: `ADD X`
   Adds the value in memory address X to the accumulator.

4. SUB: `SUB X`
   Subtracts the value in memory address X from the accumulator.

5. HALT: `HALT`
   Stops program execution.

6. IN: `IN`
   Waits for user input and stores the ASCII value of the first character in the accumulator.

7. DISP: `DISP`
   Displays the character represented by the accumulator value at the current cursor position.

8. CURS: `CURS`
   Sets the cursor position based on the accumulator value. Lower 4 bits for X, upper 4 bits for Y.

9. CLR: `CLR`
   Clears the display and resets the cursor to (0, 0).

## Example Program

Here's an example program that prompts for user input and displays it:

```
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
IN        ; Get user input
DISP      ; Display user input
HALT
```

This program will display "Enter: " on the screen, wait for user input, and then display the entered character.

## Extending the Simulation

To add new features or instructions to the computer:

1. Update the `execute` method in the `EightBitComputer` class to handle the new instruction.
2. Add the new instruction to the `opcodes` dictionary in the `Assembler` class.
3. Update the README to document the new instruction or feature.