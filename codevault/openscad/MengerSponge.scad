// Auto-generated Code Vault for 'MengerSponge' [Openscad]

// MengerSponge.scad
// Recursive 3D Menger Sponge Fractal
// WARNING: Depth 3 generates 20^3 = 8,000 cubes. Rendering may take a few seconds!

module menger_sponge(size, depth) {
    if (depth == 0) {
        // Base case: a solid cube
        cube(size, center=true);
    } else {
        s = size / 3;
        // Iterate through a 3x3x3 grid
        for (x = [-1 : 1]) {
            for (y = [-1 : 1]) {
                for (z = [-1 : 1]) {
                    // The Menger Sponge removes the center cube and the center of each face.
                    // This means we only draw a sub-cube if at least 2 out of the 3 coordinates are non-zero.
                    if ((abs(x) + abs(y) + abs(z)) >= 2) {
                        translate([x * s, y * s, z * s])
                            menger_sponge(s, depth - 1);
                    }
                }
            }
        }
    }
}

// -------------------- RENDER --------------------
// Generate a Menger Sponge of size 27 (divisible by 3) at depth 3
// Depth 1 = 20 cubes
// Depth 2 = 400 cubes
// Depth 3 = 8,000 cubes
// Depth 4 = 160,000 cubes (Not recommended unless you have a supercomputer!)

menger_sponge(size=27, depth=3);
