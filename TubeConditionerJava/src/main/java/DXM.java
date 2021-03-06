
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;



/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author mjsh6
 */
public class DXM {

    String address;
    int port;
    boolean connected = false;
    String modelNumber;
    boolean ArcPresent = false;
    boolean OverTemperature = false;
    boolean OverVoltage = false;
    boolean UnderVoltage = false;
    boolean OverCurrent = false;
    boolean UnderCurrent = false;
    boolean HighVoltageState = false;
    boolean InterlockOpen = false;
    boolean FaultPresent = false;
    boolean RemoteMode = false;


    public DXM(String address, int port) {
        this.address = address;
        this.port = port;
        this.modelNumber = this.Get_Model_Type();
        this._Update_Fault_States();
        this._Update_Status_Signals();

    }

    public String Get_Model_Type(){
        // sets the supply to remote mode, and returns the supply type in X#### format
        this._Set_Mode_Remote();
        this.connected = true;
        return this._Read_Model_Type();
    }

    public boolean Get_Interlock_Status(){
        this._Update_Status_Signals();
        return this.InterlockOpen;
    }

    public void Reset_Faults(){
        this._Send_Command(31,"");
        this._Update_Status_Signals();
    }

    public boolean Is_Emmitting(){
        this._Update_Fault_States();
        this._Update_Status_Signals();
        return this.HighVoltageState;
    }

    public ArrayList<String> Are_There_Any_Faults(){
        this._Update_Fault_States();
        ArrayList<String> Faults = new ArrayList<String>();
        if (this.ArcPresent){
            Faults.add("Arc Present");
        }
        if (this.OverTemperature){
            Faults.add("Over Temperature");
        }
        if (this.OverVoltage){
            Faults.add("Over Voltage");
        }
        if (this.UnderVoltage){
            Faults.add("Under Voltage");
        }
        if (this.OverCurrent){
            Faults.add("Over Current");
        }
        if (this.UnderCurrent){
            Faults.add("Under Current");
        }
        return Faults;
    }

    public String Read_Voltage_Out_String(){
        return this._Get_Voltage().toString();
    }

    public Double Read_Voltage_Out_Double(){
        return this._Get_Voltage();
    }

    public String Read_Current_Out_String(){
        return this._Get_Current().toString();
    }
    
    public Double Read_Current_Out_Double(){
        return this._Get_Current();
    }

    public Double[] Get_Voltage_Current_Filament(){
        String[] response = this._Send_Command(19, "");
        Double voltage = Double.parseDouble(response[1]);
        Double current = Double.parseDouble(response[2]);
        Double filCurrent = Double.parseDouble(response[3]);
        Double scaledVoltage = 0.0;
        Double scaledCurrent = 0.0;
        Double scaledFilCurrent = filCurrent * 0.001221;
        switch (this.modelNumber) {
            case "X4087":
                scaledVoltage = voltage * 0.00976;
                scaledCurrent = current * 0.007326;
                break;
            case "X3481":
                scaledVoltage = voltage * 0.007326007;
                scaledCurrent = current * 0.002442002;
                break;
            case "X4911":
                scaledVoltage = voltage * 0.00976;
                scaledCurrent = current * 0.00366300;
                break;
            case "X4313":
                scaledVoltage = voltage * 0.00732007;
                scaledCurrent = current * 0.00488400;
                break;
        }
        return new Double[] {scaledVoltage,scaledCurrent,scaledFilCurrent};
    }

    private Double _Get_Voltage(){
        // send command, and then parse response to a double.
        String[] response = this._Send_Command(19, "");
        Double voltage = Double.parseDouble(response[1]);
        Double scaledVoltage = 0.0;
        // depending on the model type, apply different weights
        switch (this.modelNumber) {
            case "X4087":
                scaledVoltage = voltage * 0.00976;
                break;
            case "X3481":
                scaledVoltage = voltage * 0.007326007;
                break;
            case "X4911":
                scaledVoltage = voltage * 0.00976;
                break;
            case "X4313":
                scaledVoltage = voltage * 0.00732007;
                break;
        }
        return scaledVoltage;
    }

    private Double _Get_Current(){
        String[] response = this._Send_Command(19, "");
        Double current = Double.parseDouble(response[2]);
        Double scaledCurrent = 0.0;
        // depending on the model type, apply different weights
        switch (this.modelNumber) {
            case "X4087":
                scaledCurrent = current * 0.007326;
                break;
            case "X3481":
                scaledCurrent = current * 0.002442002;
                break;
            case "X4911":
                scaledCurrent = current * 0.00366300;
                break;
            case "X4313":
                scaledCurrent = current * 0.00488400;
                break;
        }
        return scaledCurrent;
    }
    
    private Double _Get_Set_Preheat(){
        String[] response = this._Send_Command(17,"");
        return (Double.valueOf(response[1]) * 0.0006105);
    }

    private Double _Get_Set_Filament_Limit(){
        String[] response = this._Send_Command(16,"");
        return (Double.valueOf(response[1]) * 0.001221);
    }

    private Double _Get_Set_Voltage(){
        String[] response = this._Send_Command(14, "");
        Double voltage = Double.parseDouble(response[1]);
        Double scaledVoltage = 0.0;
        // depending on the model type, apply different weights
        switch (this.modelNumber) {
            case "X4087":
                scaledVoltage = voltage * 0.00976;
                break;
            case "X3481":
                scaledVoltage = voltage * 0.007326007;
                break;
            case "X4911":
                scaledVoltage = voltage * 0.00976;
                break;
            case "X4313":
                scaledVoltage = voltage * 0.00732007;
                break;
        }
        return scaledVoltage;
    }

    private Double _Get_Set_Current(){
        String[] response = this._Send_Command(15, "");
        Double current = Double.parseDouble(response[1]);
        Double scaledCurrent = 0.0;
        // depending on the model type, apply different weights
        switch (this.modelNumber) {
            case "X4087":
                scaledCurrent = current * 0.007326;
                break;
            case "X3481":
                scaledCurrent = current * 0.002442002;
                break;
            case "X4911":
                scaledCurrent = current * 0.00366300;
                break;
            case "X4313":
                scaledCurrent = current * 0.00488400;
                break;
        }
        return scaledCurrent;
    }

    private void _Set_Voltage(double value){
        int scaledValue = 0;
        switch (this.modelNumber) {
            case "X4087":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.0976);
                break;
            case "X3481":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.007326007);
                break;
            case "X4911":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.0976);
                break;
            case "X4313":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.007326007);
                break;
        }
        this._Send_Command(10, String.valueOf(scaledValue));
    }

    private void _Set_Current(double value){
        int scaledValue = 0;
        switch (this.modelNumber) {
            case "X4087":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.007326);
                break;
            case "X3481":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.002442002);
                break;
            case "X4911":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.00366300);
                break;
            case "X4313":
                scaledValue = (int)Math.round(Double.valueOf(value)/0.00488400);
                break;
        }
        this._Send_Command(11, String.valueOf(scaledValue));
    }

    private void _Set_Filament_Limit(double value){
        int scaledValue = (int)Math.round(Double.valueOf(value)/0.001221);
        this._Send_Command(12, String.valueOf(scaledValue)) ; 
    }

    private void _Set_Filament_Preheat(double value){
        int scaledValue = (int)Math.round(Double.valueOf(value)/0.0006105);
        this._Send_Command(13, String.valueOf(scaledValue)) ; 
    }

    private void _Update_Status_Signals(){
        /*Command to read status
        <ARG1>  1 = HvOn, 0 = HvOff
        <ARG2>  1 = Interlock 1 Open, 0 = Interlock 1 Closed
        <ARG3>  1 = Fault Condition, 0 = No Fault
        <ARG4>  1 = Remote Mode, 0 = Local Mode
        */
        String[] response = this._Send_Command(22, "");
        this.HighVoltageState = (response[2] == "1");
        this.InterlockOpen = (response[3] == "1");
        this.FaultPresent = (response[4] == "1");
        this.RemoteMode = (response[5] == "1");
        
    }

    private void _Update_Fault_States(){
        /*return args of faults
        ARG1 = ARC
        ARG2 = Over Temperature
        ARG3 = Over Voltage
        ARG4 = Under Voltage
        ARG5 = Over Current
        ARG6 = Under Current*/
        String[] response = this._Send_Command(68, "");
        this.ArcPresent = (response[2] == "1");
        this.OverTemperature = (response[3] == "1");
        this.OverVoltage = (response[4] == "1");
        this.UnderVoltage = (response[5] == "1");
        this.OverCurrent = (response[6] == "1");
        this.UnderCurrent = (response[7] == "1");
    }

    private boolean _Xray_On(){
        // command the supply to turn on xrays, returns true if command received successful
        String[] response = this._Send_Command(98, "1");
        if (response[1] == "$"){
            return true;
        }
        else{
            return false;
        }
    }

    private boolean _Xray_Off(){
        // command the supply to turn off xrays, returns true if command received successful
        String[] response = this._Send_Command(98, "0");
        if (response[1] == "$"){
            return true;
        }
        else{
            return false;
        }
    }

    private String _Read_Model_Type(){
        // call send command, and return the 1st index (this contains the model number)
        String response = this._Send_Command(26, "")[1];
        String model;
        switch (response) //if the model type is DXM based, switch to X####, else use X####
        {
            case "DXM02":
                model = "X3481";
                break;
            case "DXM20":
                model = "X413";
                break;
            case "DXM21":
                model = "X4911";
                break;
            case "DXM33":
                model = "X4087";
                break;
            default:
                model = response;
        }
        return model;
    }

    private void _Set_Mode_Remote(){
        // set the supply to remote mode
        this._Send_Command(99,"1");
    }

    private String[] _Send_Command(int Command, String Argument){
        // Send commands to the supply
        if (Argument != "") {
        // if the argument isnt blank, it requires a comma after
            Argument = Argument + ",";
        }
        String reply = "";

        try (Socket sock = new Socket(this.address,this.port)) 
        {   // open socket, create message, send message, receive response, convert to string
            String message = String.format("\002%1$s,%2$s\003", Command,Argument);
            byte[] byteResponse = new byte[40];
            byte[] byteArrayMessage = message.getBytes(StandardCharsets.US_ASCII);
            OutputStream outStream = sock.getOutputStream();
            InputStream inStream = sock.getInputStream();
            outStream.write(byteArrayMessage);
            inStream.read(byteResponse);

            reply = new String(byteResponse);
        } 
        catch (Exception e) {
            System.out.println(e);
        }
        // split response into string array
        String[] splitResponse = reply.split(",");
        //return the string array
        return splitResponse;
    }
}

