// Imports
import com.qualcomm.robotcore.eventloop.opmode.Disabled;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;

@Disabled

@TeleOp

/**
 * Test of table with gamepad
 */
public class ThreeAxisTest extends OpMode
    {    
    
    private ThreeAxisTable table;
    
    public void init()
    {
        table = new ThreeAxisTable(hardwareMap);
        table.setMode(DcMotor.RunMode.RUN_USING_ENCODER);
    }
    
    public void loop() 
    {   
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
        
        // Movement with stick
        table.setXPower(-this.gamepad1.left_stick_y);
        table.setYPower(this.gamepad1.left_stick_x);
        //table.moveZ(this.gamepad1.right_trigger);
        
        // Testing methods
        if (this.gamepad1.left_bumper) {
            table.lowerZ();
        }
        
        if (this.gamepad1.right_bumper) { 
            table.raiseZ();
        }
        
        if (this.gamepad1.left_stick_button) {
            table.setZeroMode(DcMotor.ZeroPowerBehavior.FLOAT);
        }
        
        if (this.gamepad1.right_stick_button) {
            table.setZeroMode(DcMotor.ZeroPowerBehavior.BRAKE);
        }
        
        if (this.gamepad1.x) { // Set new origin
            table.setOrigin();
        }
        
        if (this.gamepad1.y) { // Go to origin
            table.moveToOrigin();
        }
    }
}