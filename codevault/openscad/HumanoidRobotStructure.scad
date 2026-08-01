// Auto-generated Code Vault for 'HumanoidRobotStructure' [Openscad]

module HumanoidRobotStructure(){
    // Body
    module body(){
        cylinder(h = 100, r = 50, center = true);
    }
    body();

    // Head
    module head(){
        translate([0, 50, 0])
        sphere(r = 30);
    }
    head();

    // Left Arm
    module leftArm(){
        translate([-30, 20, 0])
        cube([20, 80, 20]);
    }
    leftArm();

    // Right Arm
    module rightArm(){
        translate([30, 20, 0])
        cube([20, 80, 20]);
    }
    rightArm();

    // Left Hand
    module leftHand(){
        translate([-30, -60, 0])
        sphere(r = 10);
    }
    leftHand();

    // Right Hand
    module rightHand(){
        translate([30, -60, 0])
        sphere(r = 10);
    }
    rightHand();

    // Left Leg
    module leftLeg(){
        translate([-20, -100, 0])
        cube([20, 100, 20]);
    }
    leftLeg();

    // Right Leg
    module rightLeg(){
        translate([20, -100, 0])
        cube([20, 100, 20]);
    }
    rightLeg();

    // Left Foot
    module leftFoot(){
        translate([-20, -200, 0])
        cube([20, 20, 20]);
    }
    leftFoot();

    // Right Foot
    module rightFoot(){
        translate([20, -200, 0])
        cube([20, 20, 20]);
    }
    rightFoot();
}

HumanoidRobotStructure();
