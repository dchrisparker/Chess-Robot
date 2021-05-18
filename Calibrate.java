import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;

@TeleOp

/**
 * Calibrates the robot
 * 
 * A - Sets the origin
 * Left Stick Button - Goes to origin
 * X - Sets x maximum
 * Y - Sets y maximum
 */
public class Calibrate extends OpMode {
    private ThreeAxisTable table; // Object representing the table

    // Maxima
    private int maxX = 0;
    private int maxY = 0;

    // Log object for saving calibration
    private Log log;

    /**
     * Starts program
     */
    public void init() {
        // Instantiating the table and setting the run mode
        table = new ThreeAxisTable(hardwareMap); 
        table.setMode(DcMotor.RunMode.RUN_USING_ENCODER); 
    }

    /**
     * Runs repeatedly
     */
    public void loop() {

        // Telemetry
        telemetry.addData("X", table.getXPos()); // X Axis
        telemetry.addData("X-Left", table.getXL()); // Left motor of x
        telemetry.addData("X-Right", table.getXR()); // Right
        telemetry.addData("Y", table.getYPos()); // Y Axis
        telemetry.addData("Servo", table.getZPos()); // Servo Position
        telemetry.addData("Time", time); // Total time since start
        telemetry.addData("LT", this.gamepad1.left_trigger); // Trigger values
        telemetry.addData("RT", this.gamepad1.right_trigger);
        updateTelemetry(telemetry); // Updates the telemetry (sends it to phone)

        double powerMod = 1; // Controls the speed of the motor

        if (this.gamepad1.right_bumper) { // Reduces speed when right bumper is held
            powerMod = 0.25;
        }

        // Setting power based off left stick of gamepad
        table.setXPower(this.gamepad1.left_stick_y*powerMod);
        table.setYPower(-this.gamepad1.left_stick_x*powerMod);

        if (this.gamepad1.a) { // Set new origin
            table.setOrigin();
        }

        if (this.gamepad1.left_stick_button) { // Go to origin
            table.moveToOrigin();
        }

        if (this.gamepad1.x) { // Set x maximum
            maxX = table.getXPos();
        }

        if (this.gamepad1.y) { // Set y maximum
            maxY = table.getYPos();
        }
    }

    /**
     * Runs when stop is pressed on phone
     */
    public void stop() {
        log = new Log("cal", false); // Instantiates log
        log.addData(maxX); // Adding data to log 
        log.addData(maxY);
        log.update(); // Updating the file
        log.close(); // Closing the file/log
    }
}
