package org.firstinspires.ftc.teamcode;


import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;
import java.nio.charset.StandardCharsets;
import android.os.Environment;

@TeleOp

public class TransmissionTester extends OpMode{
    private ChessBot chess;
    private final String BASE_FOLDER_NAME = "FIRST"; 
    private String filePath;

    public void init() {
        filePath = Environment.getExternalStorageDirectory().getPath()+"/"+BASE_FOLDER_NAME+"/cal.csv";
        chess = new ChessBot(hardwareMap, filePath);
    }

    public void loop() {
        byte[] stream = chess.getTransmission(8, 1);

        byte[] send;

        for (int i = 0; i < 1000; i++) {
            
        }


        telemetry.addData("InStream: ", toString(stream));
        updateTelemetry(telemetry);
    }

    private String toString(byte[] array) {
        return new String(array, StandardCharsets.UTF_8);
    }
}
