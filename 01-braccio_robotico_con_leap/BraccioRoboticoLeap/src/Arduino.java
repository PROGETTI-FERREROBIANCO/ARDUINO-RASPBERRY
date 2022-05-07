
import java.io.PrintWriter;
import java.util.concurrent.TimeUnit;

import com.fazecast.jSerialComm.*;


public class Arduino {
    private SerialPort comPort;
    private String portDescription;
    private int baud_rate;
    private PrintWriter pout;

    public Arduino() {
        //empty constructor if port undecided
    }
    public Arduino(String portDescription) {
        //make sure to set baud rate after
        this.portDescription = portDescription;
        comPort = SerialPort.getCommPort(this.portDescription);
    }

    public Arduino(String portDescription, int baud_rate) {
        //preferred constructor
        this.portDescription = portDescription;
        comPort = SerialPort.getCommPort(this.portDescription);
        this.baud_rate = baud_rate;
        comPort.setBaudRate(this.baud_rate);
    }



    public boolean openConnection(){
        if(comPort.openPort()){
            pout = new PrintWriter(comPort.getOutputStream());
            //try {Thread.sleep(100);} catch(Exception e){}
            return true;
        }
        else {
            return false;
        }
    }

    public void closeConnection() {
        comPort.closePort();
    }

    public void setPortDescription(String portDescription){
        this.portDescription = portDescription;
        comPort = SerialPort.getCommPort(this.portDescription);
    }
    public void setBaudRate(int baud_rate){
        this.baud_rate = baud_rate;
        comPort.setBaudRate(this.baud_rate);
    }

    public String getPortDescription(){
        return portDescription;
    }

    public SerialPort getSerialPort(){
        return comPort;
    }

    public void serialWrite(String s){
        //writes the entire string at once.
        try {
            TimeUnit.MILLISECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        pout.print(s);
        pout.flush();

    }

}
