; Keywords
[
  "class"
  "constructor"
  "function"
  "method"
  "field"
  "static"
  "var"
  "let"
  "do"
  "if"
  "else"
  "while"
  "return"
] @keyword

; Built-in primitive types
[
  "int"
  "char"
  "boolean"
] @type.builtin

; Constants and special variables
(true) @boolean
(false) @boolean
(null) @constant.builtin
(this) @variable.special

; Comments
(comment) @comment
(doc_comment) @comment.doc

; Literals
(integer) @number
(string) @string

; Type references (class name used as type)
(class_name) @type

; Class declaration name
(class_declaration name: (identifier) @type)

; Subroutine declaration name and return type
(subroutine_declaration name: (identifier) @function)
(subroutine_declaration type: (type) @type)

; Subroutine parameters — no field names on `parameter` node
(parameter (type) @type)
(parameter (identifier) @variable.parameter)

; Local variable declaration
(local_variable_declaration (type) @type)
(local_variable_declaration (identifier) @variable)

; Class variable declaration
(class_variable_declaration (type) @type)
(class_variable_declaration (identifier) @variable)

; Member accesses
(member_expression property: (identifier) @property)
(member_expression object: (identifier) @variable)

; Method and Function Calls
(call_expression function: (identifier) @function)
(call_expression function: (member_expression property: (identifier) @function))

; Array Subscripts
(subscript_expression object: (identifier) @variable)

; Left-hand side assignment variable (direct assignment only, not subscript targets)
(let_statement . (identifier) @variable)

; Brackets and Punctuation
[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  ","
  ";"
  "."
] @punctuation.delimiter

; Operators
[
  "="
  "+"
  "-"
  "*"
  "/"
  "&"
  "|"
  "<"
  ">"
  "~"
] @operator
