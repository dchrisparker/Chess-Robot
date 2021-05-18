package org.firsinspires.ftc.teamcode;
// Imports
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor.RunMode;

@TeleOp

/**
 * Used to set origin without changing calibration
 * 
 * Left Stick - Movement
 * Right Trigger - Slowed movement 
 * A - Set origin
 * Left Stick Button - Go to origin 
 * X - Correct x drift
 * Right Stick Button - Reset table
 * Left Bumper - Lower Z Axis
 * Right Bumper - Raise Z Axis
 */
public class Origin extends OpMode {
    private ThreeAxisTable table;

    /**
     * Runs at start
     */
    public void init() {
        table = new ThreeAxisTable(hardwareMap); // CoordinateTable is not needed
        table.setMode(RunMode.RUN_USING_ENCODER);
    }

    public void loop() {
        // Telemetry
        telemetry.addData("X", table.getXPos());
        telemetry.addData("X-Left", table.getXL());
        telemetry.addData("X-Right", table.getXR());
        telemetry.addData("Y", table.getYPos());
        telemetry.addData("Servo", table.getZPos());
        telemetry.addData("Time", time);
        telemetry.addData("LT", this.gamepad1.left_trigger);
        telemetry.addData("RT", this.gamepad1.right_trigger);
        updateTelemetry(telemetry);

        double powerMod = 1;

        if (this.gamepad1.right_trigger > 0) { // Slows table when right trigger is pressed
            powerMod = 0.25;
        }

        table.setXPower(this.gamepad1.left_stick_y*powerMod);
        table.setYPower(-this.gamepad1.left_stick_x*powerMod);

        if (this.gamepad1.a) { // Set new origin
            table.setOrigin();
        }

        if (this.gamepad1.left_stick_button) { // Go to origin
            table.moveToOrigin();
        }

        if (this.gamepad1.x) { // Set x maximum
            table.correctX();
        }

        if (this.gamepad1.right_stick_button) { // Reset
            table.reset();
        }

        if (this.gamepad1.right_bumper) { // Raise
            table.raiseZ();
        }

        if (this.gamepad1.left_bumper) { // Lower
            table.lowerZ();
        }
    }
}
