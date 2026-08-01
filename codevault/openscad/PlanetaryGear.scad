// Auto-generated Code Vault for 'PlanetaryGear' [Openscad]

module PlanetaryGear(
  sunTeeth = 10,
  planetTeeth = 20,
  ringTeeth = 60,
  pitchRadius = 20,
  thickness = 5,
  $fn = 100
) {
  // Calculate the pitch diameter
  sunPitchDiameter = pitchRadius * 2 * sunTeeth / (sunTeeth + planetTeeth);
  planetPitchDiameter = pitchRadius * 2 * planetTeeth / (sunTeeth + planetTeeth);
  ringPitchDiameter = pitchRadius * 2 * ringTeeth / (sunTeeth + planetTeeth);

  // Calculate the outer diameter
  sunOuterDiameter = sunPitchDiameter + 2;
  planetOuterDiameter = planetPitchDiameter + 2;
  ringOuterDiameter = ringPitchDiameter + 2;

  // Central sun gear
  module sunGear() {
    cylinder(h = thickness, d = sunOuterDiameter, center = true, $fn = $fn);
    for (i = [0 : sunTeeth - 1]) {
      rotate([0, 0, i * 360 / sunTeeth])
      translate([sunPitchDiameter / 2, 0, 0])
      cube([1, thickness, thickness], center = true);
    }
  }

  // Planet gear
  module planetGear() {
    cylinder(h = thickness, d = planetOuterDiameter, center = true, $fn = $fn);
    for (i = [0 : planetTeeth - 1]) {
      rotate([0, 0, i * 360 / planetTeeth])
      translate([planetPitchDiameter / 2, 0, 0])
      cube([1, thickness, thickness], center = true);
    }
  }

  // Outer ring gear
  module ringGear() {
    difference() {
      cylinder(h = thickness, d = ringOuterDiameter, center = true, $fn = $fn);
      for (i = [0 : ringTeeth - 1]) {
        rotate([0, 0, i * 360 / ringTeeth])
        translate([ringPitchDiameter / 2, 0, 0])
        cube([1, thickness, thickness], center = true);
      }
    }
  }

  // Assemble the planetary gear system
  sunGear();
  for (i = [0 : 2]) {
    rotate([0, 0, i * 120])
    translate([pitchRadius, 0, 0])
    planetGear();
  }
  ringGear();
}

// Example usage:
PlanetaryGear(sunTeeth = 10, planetTeeth = 20, ringTeeth = 60, pitchRadius = 20, thickness = 5);
