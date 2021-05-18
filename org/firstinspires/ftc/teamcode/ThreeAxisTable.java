package org.firstinspires.ftc.teamcode;
import java.util.concurrent.TimeUnit;

// Imports
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotor.*;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.hardware.Servo;
import com.qualcomm.robotcore.hardware.TouchSensor;
import com.qualcomm.robotcore.util.ElapsedTime;

/**
 * A class representing the Three(ish) Axis Table
 * 
 * Provides methods for modifying and using the table
 */
public class ThreeAxisTable {
    private DcMotor xAxisL; // Left motor of x-axis
    private DcMotor xAxisR; // Right motor of x-axis
    private DcMotor yAxis; // Motor of y-axis
    private Servo zAxis; // Servo for z-axis
    private TouchSensor button; // Button
    private HardwareMap hardwareMap; // HardwareMap object for robot things
    private double sStart; // Bottom of servo range
    private double sEnd; // Top of servo range
    protected DcMotor.RunMode cMode; // Current motor mode
    protected ElapsedTime timer;

    /**
     * Constructs new ThreeAxisTable object
     * 
     * Takes a HardwareMap object from implementation location
     * 
     * If there are errors, ensure names listed here are the same as the names on
     * the controller.
     * 
     * @param hardwareMap The HardwareMap from the class this is being implemented
     */
    public ThreeAxisTable(HardwareMap hardwareMap) {
        this.hardwareMap = hardwareMap; // Taking the
        xAxisL = (DcMotor) this.hardwareMap.get(DcMotor.class, "xAxisL");
        xAxisR = (DcMotor) this.hardwareMap.get(DcMotor.class, "xAxisR");
        yAxis = (DcMotor) this.hardwareMap.get(DcMotor.class, "yAxis");
        zAxis = (Servo) this.hardwareMap.get(Servo.class, "zAxis");
        button = (TouchSensor) this.hardwareMap.get(TouchSensor.class, "button");
        zAxis.scaleRange(Servo.MIN_POSITION, Servo.MAX_POSITION);
        sStart = 0.225;
        sEnd = 0.05;
        cMode = yAxis.getMode();


        xAxisL.setZeroPowerBehavior(ZeroPowerBehavior.BRAKE);
        xAxisR.setZeroPowerBehavior(ZeroPowerBehavior.BRAKE);
        yAxis.setZeroPowerBehavior(ZeroPowerBehavior.BRAKE);
    }

    // MOVEMENT METHODS

    // Move to position

    /**
     * Moves x to position
     * @param pos Position to move to
     */
    public void moveX(int pos) {
        // Setting target position for both axises (right is reversed so
        // Motors go in same direction
        xAxisL.setTargetPosition(pos);
        xAxisR.setTargetPosition(-pos);

        // Begins the movement of the motor and provides power
        setMode(RunMode.RUN_TO_POSITION);
        setXPower(0.25);

        // Waits for end of movement
        while (isBusy()) {
        }

        // Turns off motor and returns it to current mode
        setYPower(0);
        setMode(cMode);

    }

    /**
     * Moves y to position
     * @param pos Position to move to
     */
    public void moveY(int pos) {
        yAxis.setTargetPosition(pos);

        setMode(RunMode.RUN_TO_POSITION);
        setYPower(0.25);

        while (isBusy()) {}

        setYPower(0);
        setMode(cMode);
    }

    /**
     * Moves to x-y position (x first then y)
     * @param xPos X Position
     * @param yPos Y Position
     */
    public void move(int xPos, int yPos) {
        moveX(xPos);
        moveY(yPos);
    }

    /**
     * Moves z servo to position 
     * @param pos Double between [0,1] that represents its position
     */
    public void moveZ(double pos) {
        zAxis.setPosition(pos);
    }

    /**
     * Moves x to origin
     */
    public void moveToOriginX() {
        xAxisL.setTargetPosition(0);
        xAxisR.setTargetPosition(0);
        xAxisL.setMode(RunMode.RUN_TO_POSITION);
        xAxisR.setMode(RunMode.RUN_TO_POSITION);

        setXPower(0.75);

        while (isBusy()) {
            if (Math.abs(getXPos()) < 100) {
                setXPower(0.5);
            }
        }

        setXPower(0);

        setMode(cMode);
        setMode(cMode);
    }

    /**
     * Moves y to origin
     */
    public void moveToOriginY() {
        yAxis.setTargetPosition(0);
        yAxis.setMode(RunMode.RUN_TO_POSITION);

        setYPower(0.75);

        while (isBusy()) {
            if (Math.abs(yAxis.getCurrentPosition()) < 50) {
                yAxis.setPower(0.5);
            }
        }

        setYPower(0);

        setMode(cMode);
    }

    /**
     * Moves x and y to origin
     */
    public void moveToOrigin() {
        moveToOriginX();
        moveToOriginY();
    }

    /**
     * To be run at end of programs 
     * 
     * Method exits immediately
     */
    public void end() {
        yAxis.setTargetPosition(0);
        xAxisL.setTargetPosition(0);
        xAxisR.setTargetPosition(0);
        setMode(RunMode.RUN_TO_POSITION);

        setYPower(0.75);

    }

    /**
     * Corrects any drift between x axis motors by running the right motor to the same 
     * position as the left motor
     */
    public void correctX() {
        xAxisR.setTargetPosition(-xAxisL.getCurrentPosition());

        setMode(RunMode.RUN_TO_POSITION);
        xAxisR.setPower(0.50);

        while (isBusy()) {}


        setXPower(0);
        setMode(cMode);
    }

    /**
     * Resets table
     */
    public void reset() {
        lowerZ();
        moveToOrigin();
    }

    // Move via power

    /**
     * Sets X-Axis power
     * @param power Power
     */
    public void setXPower(double power) {
        xAxisL.setPower(power);
        xAxisR.setPower(-power);
    }

    /**
     * Sets Y-Axis power
     * @param Power
     */
    public void setYPower(double power) {
        yAxis.setPower(power);
    }

    /**
     * Sets X&Y-Axis power
     * @param power Power
     */
    public void setPower(double power) {
        setXPower(power);
        setYPower(power);
    }

    protected void setTargetPosition(int x, int y) {
        xAxisL.setTargetPosition(x);
        xAxisR.setTargetPosition(-x);
        yAxis.setTargetPosition(y);
    }

    // Z-Axis movement

    /**
     * Raises Z-Axis to max position (vertical)
     */
    public void raiseZ() {
        timer = new ElapsedTime();
        for (int pos = (int)sStart*100; pos > (int)(sEnd*100); pos--) {
            timer.reset();
            while(timer.time(TimeUnit.MILLISECONDS) < 10) {} // Waits
            zAxis.setPosition((double)pos/100);
        }
        zAxis.setPosition(sEnd);
    }

    /**
     * Lowers Z-Axis to lowest position (below horizontal)
     */
    public void lowerZ() {
        timer = new ElapsedTime();
        for (int pos = (int)sEnd*100; pos < (int)(sStart*100); pos++) {
            timer.reset();
            while(timer.time(TimeUnit.MILLISECONDS) < 10) {} // Waits
            zAxis.setPosition((double)pos/100);
        }
        zAxis.setPosition(sStart);
    }

    // ACCESSOR METHODS

    /**
     * Checks if any motor is busy
     * @return true if any motor is still moving
     */
    public boolean isBusy() {
        return xAxisL.isBusy() || xAxisR.isBusy() || yAxis.isBusy();
    }

    /**
     * Gets x position
     * @return X Position (average of two motors)
     */
    public int getXPos() {
        return (xAxisL.getCurrentPosition() - xAxisR.getCurrentPosition()) / 2;
    }

    /**
     * Gets left x motor
     * @return XL Position
     */
    public int getXL() {
        return xAxisL.getCurrentPosition();
    }

    /**
     * Gets right x motor
     * @return XR Position
     */
    public int getXR() {
        return xAxisR.getCurrentPosition();
    }

    /**
     * Gets y position
     * @return Y Position
     */
    public int getYPos() {
        return yAxis.getCurrentPosition();
    }

    /**
     * Gets z position
     * @return Z Position
     */
    public double getZPos() {
        return zAxis.getPosition();
    }

    /**
     * Gets touch sensor
     * @return Touch sensor state
     */
    public boolean getButton() {
        return button.isPressed();
    }

    // MODIFIER METHODS

    // Origin

    /**
     * Sets x origin
     */
    public void setOriginX() {

        xAxisL.setMode(RunMode.STOP_AND_RESET_ENCODER);
        xAxisR.setMode(RunMode.STOP_AND_RESET_ENCODER);

        setMode(cMode);
    }

    /**
     * Sets y origin
     */
    public void setOriginY() {
        yAxis.setMode(RunMode.STOP_AND_RESET_ENCODER);
        setMode(cMode);
    }

    /**
     * Sets origin
     */
    public void setOrigin() {
        setOriginX();
        setOriginY();
    }

    // Modes

    /**
     * Sets motors modes
     * @param mode RunMode
     */
    public void setMode(RunMode mode) {
        xAxisL.setMode(mode);
        xAxisR.setMode(mode);
        yAxis.setMode(mode);

        cMode = mode;
    }

    /**
     * Set zero power behavior
     * @param mode ZeroPowerBehavior mode
     */
    public void setZeroMode(ZeroPowerBehavior mode) {
        xAxisL.setZeroPowerBehavior(mode);
        xAxisR.setZeroPowerBehavior(mode);
        yAxis.setZeroPowerBehavior(mode);

    }
}