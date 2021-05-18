package org.firstinspires.ftc.teamcode;
// Imports
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.util.ElapsedTime;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;

import android.os.Environment;

@TeleOp

/**
 * Test of CoordinateTable using gamepad
 */
public class CoordinateTraversal extends OpMode {
    private final String BASE_FOLDER_NAME = "FIRST"; 
    private String filePath;

    private CoordinateTable table;
    private ElapsedTime timer;
    private int row = 0;
    private int col = 0;
    
    private boolean up = false;
    private boolean down = false;
    private boolean left = false;
    private boolean right = false;


    /**
     * Ran at startup
     */
    public void init() {
        filePath = Environment.getExternalStorageDirectory().getPath()+"/"+BASE_FOLDER_NAME+"/cal.csv";
        table = new CoordinateTable(8, 8, hardwareMap, filePath);
        timer = new ElapsedTime();
    }

    /**
     * Confirms origin is set and creates a new coordinate system
     */
    public void start() {
        table.moveToOrigin();
        
    }

    /**
     * Moves robot based off d-pad input
     */
    public void loop() {

        if (this.gamepad1.dpad_right) {
            //col += 1;
            right = table.moveRight();
            //table.setPositionMove(row, col);
        }
        if (this.gamepad1.dpad_left) {
            //col -= 1;
            left = table.moveLeft();
            //table.setPositionMove(row, col);
        }
        if (this.gamepad1.dpad_up) {
            //row += 1;
            up = table.moveUp();
            //table.setPositionMove(row, col);
        }
        if (this.gamepad1.dpad_down) {
            //row -= 1;
            down = table.moveDown();
            //table.setPositionMove(row, col);
        } 
        if (this.gamepad1.right_bumper) {
            table.setPositionMove(table.getRow()+1, table.getCol()+1);
        }
        if (this.gamepad1.left_bumper) {
            table.setPositionMove(table.getRow()-1, table.getCol()-1);
        }
        if (this.gamepad1.right_trigger > 0) {
            table.moveHalfRight();
        }
        if (this.gamepad1.left_trigger > 0) {
            table.moveHalfLeft();
        }
        if (this.gamepad1.left_stick_button) {
            table.center();
        }
        
        timer.reset();
        while (timer.milliseconds()<150) {} // Wait to avoid double input
        
        // Telemetry
        telemetry.addData("Row", table.getRow()+1);
        telemetry.addData("Column", table.getCol()+1);
        telemetry.addData("X Coord", table.getCoords(row, col)[0]);
        telemetry.addData("Y Coord", table.getCoords(row, col)[1]);
        telemetry.addData("Up", up);
        telemetry.addData("Down", down);
        telemetry.addData("Left", left);
        telemetry.addData("Right", right);
        telemetry.addData("PATH", filePath);
        telemetry.addData("", table.toString());
        

        updateTelemetry(telemetry);

    }

    /**
     * Runs at end of program
     */
    public void stop() {
        table.lowerZ();
        table.end();
    }
}
