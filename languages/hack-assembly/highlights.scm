; Comments
(comment) @comment

; A-instruction symbol (generic; the more specific patterns below take precedence)
(a_instruction (symbol) @variable)

; Jump Instructions
(jump) @keyword

; Predefined Symbols (Registers, I/O)
(predefined_symbol) @constant.builtin

; The pinned grammar's register pattern does not match R1 on its own
((user_symbol) @constant.builtin
  (#eq? @constant.builtin "R1"))

; Constants
(constant) @number

; Labels
(label_declaration (symbol) @label)

; Destination registers in C-instruction
(dest) @variable.parameter

; Computations
(comp) @operator
