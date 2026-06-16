// Computes R2 = R0 * R1
@R2
M=0     // Initialize R2 = 0

@R0
D=M
@END
D;JEQ   // If R0 == 0, end

@R1
D=M
@END
D;JEQ   // If R1 == 0, end

(LOOP)
@R0
D=M
@R2
M=D+M   // R2 = R2 + R0

@R1
M=M-1   // R1 = R1 - 1
D=M
@LOOP
D;JGT   // If R1 > 0, repeat

(END)
@END
0;JMP   // Infinite loop
