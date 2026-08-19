// Auto-generated Code Vault for 'SpiralStaircase' [Openscad]

// SpiralStaircase.scad
// Parametric spiral staircase with central pole, rotating steps, and handrail
// Author: OpenSCAD Senior Engineer
// Version: 1.0
// -------------------------------------------------------------

// ------------------- User Parameters -------------------------
steps          = 30;      // total number of steps
step_height    = 20;      // vertical rise per step (mm)
step_angle     = 12;      // rotation per step (degrees)
radius_inner   = 30;      // radius of central pole (mm)
radius_outer   = 100;     // outer radius of staircase (mm)
tread_depth    = radius_outer - radius_inner; // radial depth of each step
step_width     = 30;      // width of each step (mm) – perpendicular to radial direction
step_thickness = 2;       // thickness of step tread (mm)

pole_radius    = radius_inner; // central pole radius matches inner radius
pole_extra_h   = 20;            // extra height for pole above last step

handrail_radius   = 2;          // radius of handrail tube (mm)
handrail_offset   = 5;          // distance from outer edge to handrail centre (mm)
handrail_segments = 200;        // resolution of handrail helix

$fn = 64; // default resolution for circles

// ------------------- Main Assembly ---------------------------
SpiralStaircase();

module SpiralStaircase()
{
    // Central supporting pole
    translate([0,0,0])
        cylinder(h = steps*step_height + step_thickness + pole_extra_h,
                 r = pole_radius,
                 center = false);
    
    // Generate steps
    for (i = [0 : steps-1])
    {
        rotate(i*step_angle)
            translate([radius_inner, -step_width/2, i*step_height])
                Step();
    }
    
    // Handrail
    Handrail();
}

// ------------------- Step Definition ------------------------
module Step()
{
    // Simple rectangular tread extending radially outward
    // Positioned so inner edge sits on the central pole
    cube([tread_depth, step_width, step_thickness], center = false);
}

// ------------------- Handrail Definition --------------------
module Handrail()
{
    // Helical handrail approximated by a series of hulled spheres
    // Loop creates smooth tube around outer edge of staircase
    for (i = [0 : handrail_segments-1])
    {
        // First point on helix
        t1 = i / handrail_segments;
        a1 = t1 * steps * step_angle;          // cumulative angle in degrees
        z1 = t1 * steps * step_height;         // height at this point
        x1 = (radius_outer + handrail_offset) * cos(a1);
        y1 = (radius_outer + handrail_offset) * sin(a1);
        
        // Second point on helix
        t2 = (i+1) / handrail_segments;
        a2 = t2 * steps * step_angle;
        z2 = t2 * steps * step_height;
        x2 = (radius_outer + handrail_offset) * cos(a2);
        y2 = (radius_outer + handrail_offset) * sin(a2);
        
        // Hull two neighboring spheres to form a tube segment
        hull()
        {
            translate([x1, y1, z1]) sphere(r = handrail_radius);
            translate([x2, y2, z2]) sphere(r = handrail_radius);
        }
    }
}
