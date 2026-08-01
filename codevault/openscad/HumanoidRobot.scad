// Auto-generated Code Vault for 'HumanoidRobot' [Openscad]

module HumanoidRobot() {
    // Body
    cylinder(h = 120, r = 20, center = true);

    // Head
    translate([0, 0, 60])
    sphere(r = 20);

    // Legs
    translate([0, 0, -60])
    for (i = [-1, 1]) {
        translate([i * 20, 0, 0])
        cylinder(h = 60, r = 10, center = true);
    }

    // Arms
    translate([0, 0, 30])
    for (i = [-1, 1]) {
        translate([i * 20, 0, 0])
        cylinder(h = 30, r = 5, center = true);
    }
}

HumanoidRobot();
