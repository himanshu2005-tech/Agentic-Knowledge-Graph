// Auto-generated Code Vault for 'PlanetaryGearSystem' [Openscad]

module tooth(pitch_radius, tooth_width, thickness) {
    angle = 360 / (pitch_radius / tooth_width);
    rotate([0, 0, -angle/2])
    difference() {
        union() {
            cylinder(h = thickness, r = pitch_radius + tooth_width/2, $fn = 100);
            cylinder(h = thickness, r = pitch_radius - tooth_width/2, $fn = 100);
        }
        cylinder(h = thickness + 1, r = pitch_radius - tooth_width/2, $fn = 100);
    }
}

module gear(pitch_radius, tooth_width, thickness, num_teeth) {
    angle = 360 / num_teeth;
    for (i = [0 : num_teeth - 1]) {
        rotate([0, 0, i * angle])
        tooth(pitch_radius, tooth_width, thickness);
    }
}

module planetary_gear_system(sun_pitch_radius, planet_pitch_radius, ring_pitch_radius, tooth_width, thickness) {
    assert(ring_pitch_radius == sun_pitch_radius + 2 * planet_pitch_radius);
    
    // Sun gear
    color("blue")
    gear(sun_pitch_radius, tooth_width, thickness, sun_pitch_radius / tooth_width);
    
    // Planet gears
    color("red")
    for (i = [0 : 2]) {
        rotate([0, 0, i * 120])
        translate([sun_pitch_radius + planet_pitch_radius, 0, 0])
        gear(planet_pitch_radius, tooth_width, thickness, planet_pitch_radius / tooth_width);
    }
    
    // Ring gear
    difference() {
        color("green")
        cylinder(h = thickness, r = ring_pitch_radius, $fn = 100);
        color("green")
        gear(ring_pitch_radius - tooth_width/2, tooth_width, thickness + 1, ring_pitch_radius / tooth_width);
    }
}

planetary_gear_system(20, 15, 50, 3, 5);
