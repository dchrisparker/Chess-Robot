package org.firstinspires.ftc.teamcode;
import com.qualcomm.robotcore.eventloop.opmode.Autonomous;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.util.ElapsedTime;

import android.os.Environment;

public class ChessBot {
    private final String PATH;

	private CoordinateTable table; 
    private int row;
    private int col;

    public ChessBot(String path, HardwareMap hardwareMap) {
        PATH = path;
        table = new CoordinateTable(8, 8, hardwareMap, PATH);

    }
}