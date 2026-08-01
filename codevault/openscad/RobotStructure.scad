// Auto-generated Code Vault for 'RobotStructure' [Openscad]

module RobotStructure(baseWidth, baseDepth, baseHeight, pillarHeight, armLength, armWidth, armHeight) {
    // Base of the robot
    module base() {
        cube([baseWidth, baseDepth, baseHeight], center = true);
    }

    // Pillars of the robot
    module pillars() {
        translate([baseWidth/2 - 10, baseDepth/2 - 10, baseHeight/2])
            cylinder(h = pillarHeight, r = 5, center = true);
        translate([baseWidth/2 - 10, -baseDepth/2 + 10, baseHeight/2])
            cylinder(h = pillarHeight, r = 5, center = true);
        translate([-baseWidth/2 + 10, baseDepth/2 - 10, baseHeight/2])
            cylinder(h = pillarHeight, r = 5, center = true);
        translate([-baseWidth/2 + 10, -baseDepth/2 + 10, baseHeight/2])
            cylinder(h = pillarHeight, r = 5, center = true);
    }

    // Arms of the robot
    module arms() {
        translate([baseWidth/2 - 10, baseDepth/2 - 10, baseHeight/2 + pillarHeight/2])
            cube([armWidth, armLength, armHeight], center = true);
        translate([baseWidth/2 - 10, -baseDepth/2 + 10, baseHeight/2 + pillarHeight/2])
            cube([armWidth, armLength, armHeight], center = true);
        translate([-baseWidth/2 + 10, baseDepth/2 - 10, baseHeight/2 + pillarHeight/2])
            cube([armWidth, armLength, armHeight], center = true);
        translate([-baseWidth/2 + 10, -baseDepth/2 + 10, baseHeight/2 + pillarHeight/2])
            cube([armWidth, armLength, armHeight], center = true);
    }

    // Assemble the robot structure
    base();
    pillars();
    arms();
}

// Example usage
RobotStructure(100, 100, 20, 50, 50, 10, 10);
