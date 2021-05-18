package depreciated;
import com.qualcomm.robotcore.eventloop.opmode.Disabled;
//import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
//import com.qualcomm.robotcore.hardware.DcMotor;

//import ThreeAxisTable;
@Deprecated
@Disabled
@TeleOp

/**
 * Test of CoordinateSystem with gamepad
 */
public class CoordinateTraversalCopy /*extends OpMode*/ {

    // private ThreeAxisTable table;
    // private CoordinateSystemCopy board;
    // private int maxX;
    // private int bLX;
    // private int bLY;
    // private int tRX;
    // private int tRY;
    // private Square[][] b = new Square[8][8];
    // private int row = 0;
    // private int col = 0;
    // private Square s = new Square("", 0, 0);
    // private int moveX = 0;
    // private int moveY = 0;

    // public void init() {
    //     table = new ThreeAxisTable(hardwareMap);
    //     table.setMode(DcMotor.RunMode.RUN_USING_ENCODER);
    // }

    // /**
    //  * Used to calibrate the robot on startup
    //  */
    // public void init_loop() {
    //     telemetry.addData("X", table.getXPos());
    //     telemetry.addData("X-Left", table.getXL());
    //     telemetry.addData("X-Right", table.getXR());
    //     telemetry.addData("Y", table.getYPos());
    //     telemetry.addData("Servo", table.getZPos());
    //     telemetry.addData("Time", time);
    //     telemetry.addData("LT", this.gamepad1.left_trigger);
    //     telemetry.addData("RT", this.gamepad1.right_trigger);
    //     updateTelemetry(telemetry);

    //     table.setXPower(this.gamepad1.left_stick_y);
    //     table.setYPower(-this.gamepad1.left_stick_x);
    //     // table.moveZ(this.gamepad1.right_trigger);

    //     //if (this.gamepad1.left_bumper) {
    //     //    table.lowerZ();
    //     //}

    //     //if (this.gamepad1.right_bumper) { // Down
    //     //    table.raiseZ();
    //     //}

    //     if (this.gamepad1.x) { // Set new origin
    //         table.setOrigin();
    //     }

    //     if (this.gamepad1.a) { // Go to origin
    //         table.moveToOrigin();
    //     }

    //     if (this.gamepad1.y) { // Set x maximum
    //         maxX = table.getXPos();

    //     }
    //     if (this.gamepad1.left_bumper) {
    //         bLX = table.getXPos();
    //         bLY = table.getYPos();
    //     }
    //     if (this.gamepad1.right_bumper) {
    //         tRX = table.getXPos();
    //         tRY = table.getYPos();
    //     }
    // }

    // /**
    //  * Confirms origin is set and creates a new coordinate system
    //  */
    // public void start() {
    //     table.setOrigin();

    //     board = new CoordinateSystemCopy(b, bLX-tRX, tRY-bLY, maxX);

    //     for (int row = 0; row < b.length; row++) {
    //         for (int col = 0; col < b[0].length; col++) {
    //             board.setSquare("#", row, col);

    //             if (row == 1 || row == 6) {
    //                 board.getSquare(row, col).piece = "p";
    //             }

    //             if (row == 0 || row == 7) {
    //                 switch (col) {
    //                     case 0:
    //                     case 7:
    //                         board.getSquare(row, col).piece = "r";
    //                         break;
    //                     case 1:
    //                     case 6:
    //                         board.getSquare(row, col).piece = "b";
    //                         break;
    //                     case 2:
    //                     case 5:
    //                         board.getSquare(row, col).piece = "n";
    //                         break;
    //                     case 3:
    //                         board.getSquare(row, col).piece = "k";
    //                         break;
    //                     case 4:
    //                         board.getSquare(row, col).piece = "q";
    //                         break;
    //                 }
    //             }
    //         }
    //     }

    // }

    // /**
    //  * Moves robot based off d-pad input
    //  */
    // public void loop() {
    //     telemetry.addData("Row", row + 1);
    //     telemetry.addData("Column", col + 1);
    //     telemetry.addData("Square Size X", board.getSquareSizeX());
    //     telemetry.addData("Square Size Y", board.getSquareSIzeY());
    //     telemetry.addData("Current Square", s.piece);
    //     telemetry.addData("Square X", s.x);
    //     telemetry.addData("Square Y", s.y);
    //     telemetry.addData("MoveX", moveX);
    //     telemetry.addData("MoveY", moveY);
    //     telemetry.addData("bLX", bLX);
    //     telemetry.addData("bLY", bLY);
    //     telemetry.addData("tRX", tRX);
    //     telemetry.addData("tRY", tRY);

    //     updateTelemetry(telemetry);

    //     try {

    //         if (this.gamepad1.dpad_right) {
    //             col += 1;
    //             Thread.sleep(100);
    //         }
    //         if (this.gamepad1.dpad_left) {
    //             col -= 1;
    //             Thread.sleep(100);
    //         }
    //         if (this.gamepad1.dpad_up) {
    //             row += 1;
    //             Thread.sleep(100);
    //         }
    //         if (this.gamepad1.dpad_down) {
    //             row -= 1;
    //             Thread.sleep(100);
    //         }
    //         Thread.sleep(150);
    //     } catch (Exception InterruptedException) {

    //     }

    //     s = board.getSquare(row, col);

    //     if (s.x != moveX || s.y != moveY) {
    //         moveX = s.x;
    //         moveY = s.y;

    //         table.move(moveX, moveY);
    //     } else {
    //         table.setXPower(0);
    //         table.setYPower(0);
    //     }

    // }

    // public void stop() {
    //     table.moveToOrigin();
    //     table.raiseZ();
    // }
}
