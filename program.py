
program = """
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

    ; Check for input (you may need to implement this)
    IN
    JZ MAIN_LOOP  ; If no input, continue loop
    HALT  ; If input detected, halt the program


"""
