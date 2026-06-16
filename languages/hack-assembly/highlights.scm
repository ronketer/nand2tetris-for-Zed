; Comments
(comment) @comment

; Jump Instructions
(jump) @keyword

; Predefined Symbols (Registers, I/O)
(predefined_symbol) @constant.builtin

; Constants
(constant) @number

; Labels
(label_declaration (symbol) @label)

; Destination registers in C-instruction
(dest) @variable.parameter

; Computations
(comp) @operator

; A-instruction symbol
(a_instruction (symbol) @variable)
