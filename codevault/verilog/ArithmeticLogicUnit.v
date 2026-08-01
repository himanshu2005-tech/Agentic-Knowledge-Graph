// Auto-generated Code Vault for 'ArithmeticLogicUnit' [Verilog]

`timescale 1ns/1ps

module ArithmeticLogicUnit(
    input  wire [7:0] operand_a,
    input  wire [7:0] operand_b,
    input  wire [2:0] opcode,
    output wire [7:0] result,
    output wire        zero,
    output wire        carry_out
);

    wire [7:0] add_result;
    wire [7:0] sub_result;
    wire        add_carry_out;
    wire        sub_carry_out;

    assign add_result = operand_a + operand_b;
    assign sub_result = operand_a - operand_b;

    assign add_carry_out = (operand_a[7] & operand_b[7] & ~add_result[7]) | 
                           (~operand_a[7] & ~operand_b[7] & add_result[7]);
    assign sub_carry_out = (operand_a[7] & ~operand_b[7] & ~sub_result[7]) | 
                           (~operand_a[7] & operand_b[7] & sub_result[7]);

    assign carry_out = (opcode == 3'b000) ? add_carry_out : 
                        (opcode == 3'b001) ? sub_carry_out : 1'b0;

    always @(*) begin
        case(opcode)
            3'b000: result = operand_a + operand_b; // Addition
            3'b001: result = operand_a - operand_b; // Subtraction
            3'b010: result = operand_a & operand_b; // Bitwise AND
            3'b011: result = operand_a | operand_b; // Bitwise OR
            3'b100: result = operand_a ^ operand_b; // XOR
            default: result = 8'b0;
        endcase
    end

    assign zero = (result == 8'b0) ? 1'b1 : 1'b0;

endmodule
