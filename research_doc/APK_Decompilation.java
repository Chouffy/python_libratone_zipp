/* 
Decompilation & interpretation of the communication between the Anroid Libratone app and the speaker
* Not 100% accurate, goal is to have an idea of each function
* Try/catch statements have been removed
* Decompiled using JADX
*/

com.libratone.v3.luci.LUCIControl

    private static final int LUCI_CONTROL_PORT = 7777;
    private static final int LUCI_NOTIFY_RSK = 3334;
    public static final int LUCI_RESP_PORT = 3333;
    public static final int PRT_PKT = 2;
    public static final int RESEND_PKT = 3;

    public LUCIControl (String str)
        Define some var
        Get local network address
        If the local address is not null
            SendCommand(3, localV4Address.getHostAddress() + ",3333", 2);
            this.serverThread = new Thread(new ServerThread());
            this.serverThread.start();
        
    public void SendCommand (int i, String str, int i2) 
        LUCIPacket lUCIPacket = new LUCIPacket(str, (short) i, (byte) i2);
            // with volume: i=64, str='', i2=1 - this create packet with
                // commandtype = i2 = 1
        SendPacket(this.SERVER_IP, LUCI_CONTROL_PORT, lUCIPacket, false);
        

    public static void SendPacket(String SERVER_IP, int LUCI_CONTROL_PORT, LUCIPacket lUCIPacket, boolean z)
        int ba_lenght = lUCIPacket.getlength();
        byte[] byteArray = new byte[ba_lenght];
        lUCIPacket.getPacket(byteArray);
        if (LUCI_CONTROL_PORT != LUCI_NOTIFY_RSK && !z) {
            manageSentPacket(0, SERVER_IP, lUCIPacket, SERVER_IP, LUCI_CONTROL_PORT);
        }
        try {
            inetAddress = InetAddress.getByName(SERVER_IP);
        } catch (UnknownHostException e) {
            e.printStackTrace();
            inetAddress = null;
        }
        UdpMonitor.getInstance().udpSendQueue.add(new DatagramPacket(byteArray, ba_lenght, inetAddress, LUCI_CONTROL_PORT));


    class ServerThread implements Runnable {
        UnicastSocket.bind (local adress, LUCI_RESP_PORT)
        While LUCIControl !shutdown
            Receive datagram
            Extract host and data
            Log "received a response" from host + data.substring(0, 100)
            Put data in a new lUCIPacket
            If LUCIControl.this.m_handler != null
                Create new Message()
                message.what = 97;
                message.obj = lUCIPacket;
                LUCIControl.this.m_handler.sendMessage(message);



com.libratone.v3.luci.LUCIPacket

// Below is pseudo-description of each function
// If the function isn't here, then it's a very simple one

public class LUCIPacket {

    private static final String TAG = null;
    public short CRC;
    public short Command;
    public byte CommandStatus;
    public byte CommandType;
    public short DataLen;
    static int HEADER_SIZE = 10; // Define size of Header
    public byte[] header; //bArr2
    public int payload_size;
    public byte[] payload; //bArr
    public int remoteID; // Seems always 43690 when creating packet


    public LUCIPacket(String str, short s, byte b)
        If str != null, init(str.getBytes("UTF-8"), s, b); // tranform str in bytesarray and call init()

    public LUCIPacket(byte[] bArr, short s) // Call init(bArr, s)

    public void init(byte[] bArr, short s, byte b) {
    // call init (bArr, s) but with a defined bArr2[2] to b
        bArr2[2] = this.CommandType; // b or 2 . b=1 for fetchVolume
        // Otherwise same than following function

    public void init(byte[] bArr, short s) {
    /*  calculate this.header (10 bytes)
        copy bArr into this.payload
        calculate this.payload_size = bArr.length;
        define this.CRC as (Random().nextInt(65534) + 1)
    */

        // bArr comes from the calling function

        // bArr2 = this.header
            byte[] this.header = new byte[HEADER_SIZE];
            
            /* How to differentiate high and low byte in 2-byte word w:
            high_w = (w & 65280) >> 8 = (w & 0b1111111100000000) >> 8
            low_w = w & 255 = w & 0b11111111
            */

            this.header = 0x aaaa??abcd??abcdabcdxxx
                          0x aaaa................ = Remote ID = 43690
                             ....??.............. = this.CommandType = b if available, or 2
                             ......abcd.......... = this.Command = s
                             ..........??........ = this.CommandStatus = 0 but can be set with setCommandStatus
                             ............abcd.... = nextInt = this.CRC = Random().nextInt(65534) + 1
                             ................abcd = this.DataLen = s2 = this.payload_size = bArr.lenght
                        
                        // "play" command            
                        0x   00000200280000000004504c4159
                             ||||                           = remote ID = 0
                                 ||                         = commandtype = 0x02 = 2
                                   ||||                     = Command = 0x0028 = 40
                                       ||                   = CommandStatus = 0x00 = 
                                         ||||               = CRC = 0x0000 = 0
                                             ||||           = DataLen = 0x0004 = 4 = 4 char   | it is 5 for Pause      
                                                 ||||||||   = Data = 0x504c4159 = "PLAY"      | "PAUSE"
                                             
            // detail
                // i = remoteID = 43690 = 0xaaaa
                bArr2[0] = 0xaa // high byte of remoteID
                bArr2[1] = 0xaa // low byte of remote ID

                bArr2[2] = this.CommandType; // b if available otherwise 2

                // s = this.Command = s
                bArr2[3] = // high byte of s
                bArr2[4] = // low byte of s

                bArr2[5] = this.CommandStatus; // 0 but can be set with setCommandStatus

                // nextInt = this.CRC = Random().nextInt(65534) + 1
                bArr2[6] = // high byte of nextInt
                bArr2[7] = // low byte of nextInt

                // this.DataLen = s2 = this.payload_size = bArr.lenght
                bArr2[8] = // high byte of bArr.lenght
                bArr2[9] = // low byte of bArr.lenght

        // the whole last part is about copying bArr into bArr3 which is this.payload
            // bArr3 = this.payload defined if bArr.lenght > 0
                byte[] bArr3 = new byte[length];
                this.payload = bArr3;
                System.arraycopy(bArr, 0, bArr3, 0, length);
                /* arraycopy(Object src, int srcPos, Object dest, int destPos, int length)
                    src − This is the source array.
                    srcPos − This is the starting position in the source array.
                    dest − This is the destination array.
                    destPos − This is the starting position in the destination data.
                    length − This is the number of array elements to be copied.
                */

    public LUCIPacket(byte[] bArr) {
    // init but in reverse, in order to extract data from packet
    public int getpayload(byte[] bArr) {
    // return payload_size (?)
    public int getoppositepayload(byte[] bArr) {
    // return the payload but in the other direction
    public int getpayload_length() {
    // return payload_size
    public int getlength() {
    // return payload_size + HEADER_SIZE = bArr.length+10
    public int getremoteID() {
    // return remoteID = 43690
    public void setCommand(byte b) {
    // set CommandType and header[2] to b
    public void setCommandStatus(int i) {
    // set CommandStatus = header[5] to byte(i)
    public int getPacket(byte[] bArr) {
    // Copy header into bArr, with the size of header size (10)
    // if payload_size > 0, copy payload in bArr at Header_size for size payload_size
    // Return payload_size + header_size

com.libratone.v3.luci.UdpMonitor

public class UdpMonitor {

    LUCI_NOTIFY_PORT = LUCIControl.LUCI_RESP_PORT = 3333

    public static synchronized UdpMonitor getInstance() {
    // call UdpMonitor (and setHotel)
    private UdpMonitor() {
    /*  create new thread of UdpSend
        create new thread of UdpMonitor.updateNodes and then .start
        call CommandController.searchOldDevice */
    public static void setHotel() {
    // set HTTP_VER, SL_NOTIFY, SL_MSEARCH, SL_OK
    public synchronized void start() {
    /*  if mRunning is False:
        set mRunning to True
        call setOnPlayListener(CommandController.getCommandCallback());
        try createSockets()
    */

    ... to be continued

com.libratone.v3.model.LSSDPNode

    public void fetch(int i) {
    public void fetch(int i, String str) {
    // Call lUCIControl.SendCommand
        LUCIControl lUCIControl = new LUCIControl();
        lUCIControl.setSERVER_IP(getIP());
        lUCIControl.SendCommand(i, str, 1); // with i=64 and str='' for fetchVolume i.e.


    


/* Notes on UPnP
1. Adressing by DHCP
1. Advertisement on multicast UDP 239.255.255.250:1900 (HTTPMU / SSDP)
1. Description by reading XML of each device
* Responses on unicast UDP (HTTPU)
*/

fetch table in com.libratone.v3.model.LSSDPNode

i, str | hexa |  function
-|-
5 | fetchVersion - the only command the speaker answer in sleep?
51 | fetchPlayStatus
64 | 0x0040| fetchVolume
90 | fetchDeviceName
512, str | setSpeakerStereoType(str)
515 | fetchSpeakerStereoType
524 | fetchAllVoicing
260 | fetchBTCallStatus
-184, ByteBuffer.wrap(new byte[]{b}));
 | fetchDeviceTest
 IDCONST.SET_DEVICE_TEST, byteBuffer | setDeviceTest(byteBuffer)
125, str2 | setWiFiCredentials(network, str)