package org.firstinspires.ftc.teamcode;

import com.qualcomm.robotcore.hardware.I2cDeviceSynch;
import com.qualcomm.robotcore.hardware.I2cDeviceSynchDevice;
import com.qualcomm.robotcore.hardware.I2cAddr;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.util.ElapsedTime;
import com.qualcomm.robotcore.hardware.configuration.annotations.*;
import com.qualcomm.robotcore.hardware.ControlSystem;


public class ArduinoI2C extends I2cDeviceSynchDevice<I2cDeviceSynch> {
    private final I2cAddr ADDRESS_I2C_DEFAULT = new I2cAddr(8);

    @I2cDeviceType
    @DeviceProperties(description = "a device for communicating between a desktop and the control hub", 
        compatibleControlSystems = ControlSystem.REV_HUB, name = "Arduino Slave Sender/Receiver", xmlTag = "Arduino")

    public ArduinoI2C(I2cDeviceSynch deviceClient)
    {
        super(deviceClient, true);

        this.deviceClient.setI2cAddress(ADDRESS_I2C_DEFAULT);

        super.registerArmingStateCallback(false);
        this.deviceClient.engage();
    }


    @Override
    public Manufacturer getManufacturer()
    {
        return Manufacturer.Other;
    }

    @Override
    protected synchronized boolean doInitialize()
    {
        return true;
    }

    @Override
    public String getDeviceName()
    {
        return "Arduino Uno I2C Communication Device";
    }
}   
