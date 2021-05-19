package org.firstinspires.ftc.teamcode;

import com.qualcomm.robotcore.hardware.I2cDeviceSynch;
import com.qualcomm.robotcore.hardware.I2cDeviceSynchImpl;
import com.qualcomm.robotcore.hardware.I2cAddr;
import com.qualcomm.robotcore.eventloop.opmode.Autonomous;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.util.ElapsedTime;
import java.nio.charset.StandardCharsets;


//import org.firstinspires.ftc.teamcode.wire.*;

import android.os.Environment;

public class ChessBot {
    I2cDeviceSynch arduino;
    I2cDeviceSynchImpl arduinoReader;
    int ardAddress = 32;
    I2cAddr ardAddr;

    private char[][] pieces;
    private CoordinateTable table; 
    //private Wire wire;
    private int row;
    private int col;

    public ChessBot(HardwareMap hardwareMap, String path) {
        table = new CoordinateTable(8, 8, hardwareMap, path);
        pieces = new char[][]
        {   
        {'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'},
        {'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'},
        {' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '},
        {' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '},
        {' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '},
        {' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '},
        {'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'},
        {'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'}
        };
        
        ardAddr = new I2cAddr(ardAddress);

        arduino = hardwareMap.i2cDeviceSynch.get("arduino");
        arduino.engage();
        //arduinoReader = new I2cDeviceSynchImpl(arduino, ardAddr, false);
    }

    public String getMove() {
        return "";
    }

    public byte[] getTransmission(int iReg, int cReg) {
        return arduino.read(iReg,cReg);
    }

    public void sendTransmission(int iReg, byte[] b) {
        arduino.write(8, b);
    }

    public String getConInfo() {
        return arduino.getConnectionInfo();
    }
}