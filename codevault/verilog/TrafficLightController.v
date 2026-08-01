// Auto-generated Code Vault for 'TrafficLightController' [Verilog]

module TrafficLightController(
    input clk,
    input reset,
    output reg [3:0] ns_light,  // North-South light: 3 - green, 2 - yellow, 1 - red
    output reg [3:0] ew_light    // East-West light: 3 - green, 2 - yellow, 1 - red
);

// Define states for the Finite State Machine (FSM)
localparam NS_GREEN = 4'b0001;
localparam NS_YELLOW = 4'b0010;
localparam EW_GREEN = 4'b0100;
localparam EW_YELLOW = 4'b1000;

reg [3:0] state;
reg [3:0] next_state;

// Define the clock period for each state (in clock cycles)
localparam NS_GREEN_TIME = 10;
localparam NS_YELLOW_TIME = 3;
localparam EW_GREEN_TIME = 10;
localparam EW_YELLOW_TIME = 3;

reg [7:0] timer;

always @(*) begin
    case (state)
        NS_GREEN: next_state = (timer < NS_GREEN_TIME) ? NS_GREEN : NS_YELLOW;
        NS_YELLOW: next_state = (timer < NS_YELLOW_TIME) ? NS_YELLOW : EW_GREEN;
        EW_GREEN: next_state = (timer < EW_GREEN_TIME) ? EW_GREEN : EW_YELLOW;
        EW_YELLOW: next_state = (timer < EW_YELLOW_TIME) ? EW_YELLOW : NS_GREEN;
        default: next_state = NS_GREEN;
    endcase
end

always @(posedge clk or posedge reset) begin
    if (reset) begin
        state <= NS_GREEN;
        timer <= 0;
        ns_light <= 4'b0011;  // North-South red, East-West red
        ew_light <= 4'b0011;
    end else begin
        state <= next_state;
        if (next_state != state) begin
            timer <= 0;
        end else begin
            timer <= timer + 1;
        end
        case (state)
            NS_GREEN: begin
                ns_light <= 4'b0011;  // North-South green, East-West red
                ew_light <= 4'b0001;
            end
            NS_YELLOW: begin
                ns_light <= 4'b0100;  // North-South yellow, East-West red
                ew_light <= 4'b0001;
            end
            EW_GREEN: begin
                ns_light <= 4'b0001;  // North-South red, East-West green
                ew_light <= 4'b0011;
            end
            EW_YELLOW: begin
                ns_light <= 4'b0001;  // North-South red, East-West yellow
                ew_light <= 4'b0100;
            end
            default: begin
                ns_light <= 4'b0001;  // North-South red, East-West red
                ew_light <= 4'b0001;
            end
        endcase
    end
end

endmodule
