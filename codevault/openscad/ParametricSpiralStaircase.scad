// Auto-generated Code Vault for 'ParametricSpiralStaircase' [Openscad]

module ParametricSpiralStaircase(
    num_steps = 30,
    step_width = 30,
    step_depth = 10,
    step_height = 5,
    pillar_radius = 10,
    pillar_height = 200
) {
    // Draw central cylindrical pillar
    cylinder(h = pillar_height, r = pillar_radius, center = true);

    // Calculate angle increment for each step
    angle_increment = 360 / num_steps;

    // Generate steps using a for-loop
    for (i = [0 : num_steps - 1]) {
        // Calculate rotation angle and translation for current step
        rotation_angle = i * angle_increment;
        translation_z = i * step_height;

        // Draw current step
        translate([0, 0, translation_z])
        rotate([0, 0, rotation_angle])
        cube([step_width, step_depth, step_height], center = true);
    }
}

// Example usage
ParametricSpiralStaircase();
