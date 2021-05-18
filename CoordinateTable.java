// Imports
import com.qualcomm.robotcore.hardware.DcMotor.*;
import com.qualcomm.robotcore.hardware.HardwareMap;

// File imports
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.File;

/**
 * An object representing a 2/3 axis table with a coordinate system.
 * 
 * Extends ThreeAxisTable
 */
public class CoordinateTable extends ThreeAxisTable {
    private final String CALIBRATION_PATH; // Path of calibration file

    private CoordinateSystem board; // Coordinate system

    // Rows and columns 
    private int row; // Current row
    private int rowHalf; // 1 if at top of the square, 0 if center, and -1 if bottom
    private int col; // Current column
    private int colHalf; // 1 if at right of the square, 0 if center, and -1 if left
    private int maxRow; // Number of rows in coordinate system
    private int maxCol; // Number of columns in coordinate system

    /**
     * Creates a new CoordinateTable object. Requires a calibration file (.csv or similar format with
     * x coordinate as first value and y as second).
     * 
     * Will throw an error if the formatting is wrong
     * @param rows Number of rows
     * @param cols Number of columns
     * @param hardwareMap HardwareMap object from OpMode
     * @param calPath Path of the calibration file
     */
    public CoordinateTable(int rows, int cols, HardwareMap hardwareMap, String calPath) {
        super(hardwareMap); // Super (ThreeAxisTable) constructor
        super.setMode(RunMode.RUN_USING_ENCODER);

        CALIBRATION_PATH = calPath; 

        int maxX;
        int maxY;

        maxRow = rows;
        maxCol = col;
        
        // Default values (starts in center)
        rowHalf = 0; 
        colHalf = 0;
        
        try {
            // Reading from calibration file
            File file = new File(CALIBRATION_PATH);
            BufferedReader reader = new BufferedReader(new FileReader(file));
            String str = reader.readLine(); // Reading first line
            reader.close(); // Closing file/reader

            String[] strArray = str.split(","); // Splitting string int an array which should contain 2 numbers

            // Will throw an error if formatting is incorrect
            maxX = Integer.parseInt(strArray[0]); 
            maxY = Integer.parseInt(strArray[1]);

        } catch (IOException e) {
            // Defaults (will cause table to not move)
            maxX = 0;
            maxY = 0;
        }

        board = new CoordinateSystem(rows, cols, maxX, maxY); // Makes a new CoordinateSystem
    }

    // MOVEMENT METHODS

    // Straight line movement

    /**
     * Moves up one square
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveUp() {
        if (row + 1 < maxRow) { // Checks border
            row++; // Next row

            int move = board.getCoords(row, col)[0]; // Movement coordinate
            /**
             * Will be 0 if the head is in the center of a square(rowHalf==0).
             * 
             * Offset is calculated by getting half the distance between squares' centers and
             * multiplying it by the "location" of the piece on the square 1 (top), 0 (center), 
             * or -1 (bottom).
             */
            int offset = (int)Math.round((rowHalf*(board.getXJump()/2))); // Offset

            moveX(move + offset); // Move
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves down one square
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveDown() { // See moveUp()
        if (row - 1 >= 0) {
            row--; // Previous row

            int move = board.getCoords(row, col)[0];
            int offset = (int)Math.round((rowHalf*(board.getXJump()/2)));

            moveX(move + offset);
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves right one square
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveRight() {
        if (col + 1 < maxCol) {
            col++; // Next column 

            int move = board.getCoords(row, col)[1];
            /**
             * Will be 0 if the head is in the center of a square(colHalf==0).
             * 
             * Offset is calculated by getting half the distance between squares' centers and
             * multiplying it by the "location" of the piece on the square 1 (right), 0 (center), 
             * or -1 (left).
             */
            int offset = (int)Math.round((colHalf*(board.getYJump()/2)));

            moveY(move + offset); // Move
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves left one square
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveLeft() { // See moveRight();
        if (col - 1 >= 0) {
            col--; // Previous column

            int move = board.getCoords(row,col)[1];
            int offset =  (int)Math.round((colHalf*(board.getYJump()/2)));

            moveY(move + offset);
            return true;
        } else {
            return false;
        }
    }

    /**
     * Sets motor position using the provided row and column. Will not exit until
     * motor stops.
     * @param row Row to move to
     * @param col Column to move to
     */
    public void setPositionMove(int row, int col) {
        setPositionMove(row, col, 0.25); // Calls setPositionMove() with low power
    }

    // Freeform movement
    /**
     * Sets motor position using the provided row, column, and power. Will not exit until
     * motor stops.
     * @param row Row to move to
     * @param col Column to move to
     * @param power Power to move at
     */
    public void setPositionMove(int row, int col, double power) {
        // Sets target position to coordinates of square
        int[] xy = board.getCoords(row, col);
        setTargetPosition(xy[0], xy[1]);

        // Starts movement
        setMode(RunMode.RUN_TO_POSITION); 
        setPower(power);

        while (isBusy()) {} // Waits

        // Stops and returns to last mode
        setMode(cMode); 
        setPower(0);

    }

    // Diagonal movement

    /**
     * Moves at an up-right diagonal
     * 
     * CAUTION: Should not be used when head is not in center
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveUpRight() {
        if (row + 1 < maxRow && col + 1 < maxCol) { // Checks maxima
            row++; // Next row  
            col++; // Next column
            setPositionMove(row, col); // Moves
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves at an up-left diagonal
     * 
     * CAUTION: Should not be used when head is not in center
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveUpLeft() {
        if (row + 1 < maxRow && col - 1 >= 0) { // Checks maxima
            row++; // Next row
            col--; // Previous column
            setPositionMove(row, col); // Moves
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves at an down-right diagonal
     * 
     * CAUTION: Should not be used when head is not in center
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveDownRight() {
        if (row - 1 >= 0 && col + 1 < maxCol) { // Checks maxima
            row--; // Previous row
            col++; // Next column 
            setPositionMove(row, col); // Moves
            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves at an down-left diagonal
     * 
     * CAUTION: Should not be used when head is not in center
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveDownLeft() { 
        if (row - 1 >= 0 && col - 1 >= 0) { // Checks maxima
            row--; // Previous row
            col--; // Previous column 
            setPositionMove(row, col); // Moves
            return true;
        } else {
            return false;
        }
    }

    // Half-square movement
    
    /**
     * Moves half a square up
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveHalfUp() {
        if (row+1 < maxRow || rowHalf < 1) { // Checks maxima
            moveX(board.getHalfCoords(row, col, row+1, col)[0]); // Moves halfway up

            halfCheckUp(); // Updates rowHalf

            return true;
            
        } else {
            return false;
        }
    }

    /**
     * Moves half a square down
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveHalfDown() { // Checks maxima
        if (row-1 >= 0 || rowHalf > -1) {
            moveX(board.getHalfCoords(row, col, row-1, col)[0]); // Moves halfway down

            halfCheckDown(); // Updates rowHalf

            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves half a square right
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveHalfRight() {
        if (col+1 < maxCol || colHalf < 1) { // Checks maxima
            moveY(board.getHalfCoords(row, col, row, col+1)[1]); // Moves halfway right

            halfCheckRight(); // Updates colHalf

            return true;
        } else {
            return false;
        }
    }

    /**
     * Moves half a square left
     * @return True if possible or false if it would go past the maxima
     */
    public boolean moveHalfLeft() {
        if (col-1 >= 0 || colHalf > -1) { // Checks maxima
            moveY(board.getHalfCoords(row, col, row, col-1)[1]); // Moves halfway left

            halfCheckLeft(); // Updates colHalf

            return true;
        } else {
            return false;
        }
    }

    /**
     * Centers head in middle of square 
     */
    public void center() {
        setPositionMove(row, col);
    }
    
    // ACCESSOR METHODS

    /**
     * Gets coordinates from CoordinateSystem
     * @param row The row of the array (zero indexed)
     * @param col The column of the array (zero indexed)
     * @return Array containing x-y coordinates where array[0] is the x coordinate
     */
    public int[] getCoords(int row, int col) {
        return board.getCoords(row,col);
    }

    /**
     * Gets current row
     * @return Current row
     */
    public int getRow() {
        return row;
    }

    /**
     * Gets current column
     * @return Current column 
     */
    public int getCol() {
        return col;
    }

    // PRIVATE / UTIL METHODS

    /**
     * Changes rowHalf to next number and rolls over extra
     * 
     * CAUTION: Changes row if there is rollover
     */
    private void halfCheckUp() {
        switch (rowHalf) { // This isn't optimal but it works 
            case 1:
                rowHalf = -1;
                row++; // Rollover (forwards)
                break;
            case 0:
                rowHalf = 1;
                break;
            case -1:
                rowHalf = 0;
                break;
        }
    }

    /**
     * Changes rowHalf to next number and rolls over extra
     * 
     * CAUTION: Changes row if there is rollover
     */
    private void halfCheckDown() {
        switch (rowHalf) {
            case 1:
                rowHalf = 0;
                break;
            case 0:
                rowHalf = -1;
                break;
            case -1:
                rowHalf = 1;
                row--; // Rollover (backwards)
                break;
        }
    }
    
    /**
     * Changes colHalf to next number and rolls over extra
     * 
     * CAUTION: Changes row if there is rollover
     */
    private void halfCheckRight() {
        switch (colHalf) {
            case 1:
                colHalf = -1;
                col++; // Rollover (forwards)
                break;
            case 0:
                colHalf = 1;
                break;
            case -1:
                colHalf = 0;
                break;
        }
    }

    /**
     * Changes colHalf to next number and rolls over extra
     * 
     * CAUTION: Changes row if there is rollover
     */
    private void halfCheckLeft() {
        switch (colHalf) {
            case 1:
                colHalf = 0;
                break;
            case 0:
                rowHalf = -1;
                break;
            case -1:
                colHalf = 1;
                col--; // Rollover (backwards)
                break;
        }
    }
    
    /**
     * A String representation of the CoordinateSystem, formatted for ease of reading.
     * 
     * @return String
     */
    public String toString() {
        return board.toString(12);
    }
}