; Keywords
[
  "CHIP"
  "IN"
  "OUT"
  "BUILTIN"
  "CLOCKED"
  "PARTS"
] @keyword

; Numbers
(number) @number

; Comments
(comment) @comment

; Chip Definition
(chip_definition name: (identifier) @type)

; Builtin Body
(builtin_body chip_name: (identifier) @type)

; Part calls
(part chip_name: (identifier) @function)

; Connections
(connection part_pin: (identifier) @property)
(connection chip_pin: (identifier) @variable)
(connection chip_pin: (bus_identifier (identifier) @variable))
