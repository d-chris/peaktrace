# PEAK-System file format specification

&copy; by PEAK-System.com

Download: [Homepage](https://www.peak-system.com/) > Support > Downloads > Documentation

- [PEAK-System file format specification](#peak-system-file-format-specification)
  - [CAN trace files](#can-trace-files)
  - [LIN trace files](#lin-trace-files)

## CAN trace files

> [PEAK_CAN_TRC_File_Format.pdf](https://www.peak-system.com/quick/DOC-TRC-CAN)

### CAN Version 1.0

```text
;########################################################################## 
;   C:\TraceFile.trc 
; 
;    CAN activities recorded by PCAN Explorer 
;    Start time: 11.09.2002 16:00:20.682 
;    PCAN-Net: PCI1 
; 
;    Columns description: 
;    ~~~~~~~~~~~~~~~~~~~~~ 
;    +-current number in actual sample 
;    |       +time offset of message (ms) 
;    |       |         +ID of message (hex) 
;    |       |         |     +data length code 
;    |       |         |     |   +data bytes (hex) ... 
;    |       |         |     |   | 
;----+-   ---+---  ----+---  +  -+ -- -- ... 
     1)      1841      0001  8  00 00 00 00 00 00 00 00  
     2)      1842      0008  4  ERROR 00 19 08 08 
     3)      1843  FFFFFFFF  4  00 00 00 04 -- -- -- --  BUSLIGHT 
     4)      1844      0100  3  RTR 
```

### CAN Version 1.1

```text
;$FILEVERSION=1.1 
;$STARTTIME=37704.5364870833 
; 
;   C:\TraceFile.trc 
; 
;   Start time: 24.03.2003 12:52:32.484 
;   PCAN-Net: TestNet 
; 
;   Columns description: 
;   ~~~~~~~~~~~~~~~~~~~~~ 
;   +-Message Number 
;   |         +Time Offset (ms) 
;   |         |        +Type 
;   |         |        |        +ID (hex) 
;   |         |        |        |     +Data Length Code 
;   |         |        |        |     |   +Data Bytes (hex) ... 
;   |         |        |        |     |   | 
;---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- -- 
     1)      1059.9  Rx         0300  7  00 00 00 00 04 00 00  
     2)      1283.2  Rx         0300  7  00 00 00 00 04 00 00  
     3)      1298.9  Tx         0400  2  00 00  
     4)      1323.0  Rx         0300  7  00 00 00 00 06 00 00  
     5)      1346.8  Warng  FFFFFFFF  4  00 00 00 04  BUSLIGHT 
     6)      1349.2  Error      0008  4  00 19 08 08 
     7)      1352.7  Rx         0100  3  RTR 
```

### CAN Version 1.2

```text
;$FILEVERSION=1.2 
;$STARTTIME=39878.6772258947; 
;   C:\TraceFile.trc 
; 
;   Start time: 06.03.2009 16:15:12.317.3 
;   Connection: TestNet 
; 
;   Columns description: 
;   ~~~~~~~~~~~~~~~~~~~~~ 
;   +-Message Number 
;   |         +Time Offset (ms) 
;   |         |        +Bus 
;   |         |        |    +Type 
;   |         |        |    |        +ID (hex) 
;   |         |        |    |        |     +Data Length Code 
;   |         |        |    |        |     |   +Data Bytes (hex) ... 
;   |         |        |    |        |     |   | 
;---+--   ----+------  +  --+--  ----+---  +  -+ -- -- -- -- -- -- -- 
     1)      1059.900  1  Rx         0300  7  00 00 00 00 04 00 00  
     2)      1283.231  1  Rx         0300  7  00 00 00 00 04 00 00  
     3)      1298.945  1  Tx         0400  2  00 00  
     4)      1323.201  1  Rx         0300  7  00 00 00 00 06 00 00  
     5)      1346.834  1  Warng  FFFFFFFF  4  00 00 00 04  BUSLIGHT 
     6)      1349.222  1  Error      0008  4  00 19 08 08 
     7)      1352.743  1  Rx         0100  3  RTR 
```

### CAN Version 1.3

```text
;$FILEVERSION=1.3 
;$STARTTIME=40023.5245451516 
;   C:\TraceFile.trc 
; 
;   Start time: 29.07.2009 12:35:20.701.0 
;------------------------------------------------------------------------------- 
;   Bus  Name              Connection             Protocol  Bit rate 
;   1    Connection1       TestNet@pcan_usb       CAN       500 kBit/s 
;   2    Connection2       USB-Internal@pcan_usb  CAN       1 MBit/s 
;   3    J1939-1           USB1@pcan_usb          J1939     250 kBit/s 
;   4    J1939-2           USB2@pcan_usb          J1939     250 kBit/s 
;------------------------------------------------------------------------------- 
;   Message Number 
;   |         Time Offset (ms) 
;   |         |       Bus 
;   |         |       |    Type 
;   |         |       |    |       ID (hex) 
;   |         |       |    |       |    Reserved 
;   |         |       |    |       |    |   Data Length Code 
;   |         |       |    |       |    |   |    Data Bytes (hex) ... 
;   |         |       |    |       |    |   |    | 
;   |         |       |    |       |    |   |    | 
;---+-- ------+------ +- --+-- ----+--- +- -+-- -+ -- -- -- -- -- -- -- 
     1)      1059.900 1  Rx        0300 -  7    00 00 00 00 04 00 00  
     2)      1283.231 1  Rx        0300 -  7    00 00 00 00 04 00 00  
     3)      1298.945 1  Tx        0400 -  2    00 00  
     4)      1323.201 1  Rx        0300 -  7    00 00 00 00 06 00 00  
     5)      1346.834 1  Warng FFFFFFFF -  4    00 00 00 04  BUSLIGHT 
     6)      1349.222 1  Error     0008 -  4    00 19 08 08 
     7)      1352.743 1  Rx        0100 -  3    RTR 
```

### CAN Version 2.0

```text
;$FILEVERSION=2.0 
;$STARTTIME=42209.4075997106 
;$COLUMNS=N,O,T,I,d,l,D 
; 
;   C:\TraceFile.trc 
;   Start time: 24.07.2015 09:46:56.615.0 
;   Generated by PCAN-View v4.0.29.426 
;------------------------------------------------------------------------------- 
;   Connection                 Bit rate 
;   PCANLight_USB_16@pcan_usb  Nominal 1 MBit/s, Data 2 Mbit/s 
;------------------------------------------------------------------------------- 
;   Message   Time    Type ID     Rx/Tx 
;   Number    Offset  |    [hex]  |  Data Length 
;   |         [ms]    |    |      |  |  Data [hex] ... 
;   |         |       |    |      |  |  | 
;---+-- ------+------ +- --+----- +- +- +- -- -- -- -- -- -- -- 
      1      1059.900 DT     0300 Rx 7  00 00 00 00 04 00 00  
      2      1283.231 DT     0300 Rx 7  00 00 00 00 04 00 00  
      3      1298.945 DT     0400 Tx 2  00 00  
      4      1323.201 DT     0300 Rx 7  00 00 00 00 06 00 00  
      5      1334.416 FD     0500 Tx 12 01 02 03 04 05 06 07 08 09 0A 0B 0C 
      6      1334.522 ER          Rx    04 00 02 00 00 
      7      1334.531 ST          Rx    00 00 00 08 
      8      1334.643 EC          Rx    02 02 
      9      1335.156 DT 18EFC034 Tx 8  01 02 03 04 05 06 07 08 
     10      1336.543 RR     0100 Rx 3 
 
```

### CAN Version 2.1

```text
;$FILEVERSION=2.1 
;$STARTTIME=41766.4648963872 
;$COLUMNS=N,O,T,B,I,d,R,L,D 
; 
;   C:\TraceFile.trc 
;   Start time: 07.05.2015 11:09:27.047.8 
;   Generated by PCAN-Explorer v6.0.0 
;------------------------------------------------------------------------------- 
;   Bus  Name         Connection             Protocol 
;   1    Connection1  TestNet@pcan_usb       CAN 
;------------------------------------------------------------------------------- 
;   Message   Time    Type    ID     Rx/Tx 
;   Number    Offset  |  Bus  [hex]  |  Reserved 
;   |         [ms]    |  |    |      |  |  Data Length Code 
;   |         |       |  |    |      |  |  |    Data [hex] ... 
;   |         |       |  |    |      |  |  |    | 
;---+-- ------+------ +- +- --+----- +- +- +--- +- -- -- -- -- -- -- -- 
      1      1059.900 DT 1      0300 Rx -  7    00 00 00 00 04 00 00  
      2      1283.231 DT 1      0300 Rx -  7    00 00 00 00 04 00 00  
      3      1298.945 DT 1      0400 Tx -  2    00 00  
      4      1323.201 DT 1      0300 Rx -  7    00 00 00 00 06 00 00  
      5      1334.416 FD 1      0500 Tx -  9    01 02 03 04 05 06 07 08 09 0A 0B 0C 
      6      1334.222 ER 1         - Rx -  5    04 00 02 00 00 
      7      1334.224 EV 1  User-defined event for bus 1 
      8      1334.225 EV -  User-defined event for all busses 
      9      1334.231 ST 1         - Rx -  4    00 00 00 08 
     10      1334.268 ER 1         - Rx -  5    04 00 02 08 00 
     11      1334.643 EC 1         - Rx -  2    02 02 
     12      1335.156 DT 1  18EFC034 Tx -  8    01 02 03 04 05 06 07 08 
     13      1336.543 RR 1      0100 Rx -  3 
```

## LIN trace files

> [PEAK_LIN_LTRC_File_Format.pdf](https://www.peak-system.com/produktcd/Pdf/English/PEAK_LIN_LTRC_File_Format.pdf)

### LIN Version 1.0

```text
;$FILEVERSION=1.0 
;$STARTTIME=8708618495 
; 
;   C:\TraceFile.ltrc 
; 
;   Start time: 26.03.2010 11:06:08 
;   PLIN-Net: 
;    
;   Direction description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     Pub   = Publisher Frame 
;     Sub   = Subscriber Frame 
;     SubAL = Subscriber Auto Length Frame 
;    
;   Checksum Type description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     CL = Classic 
;     EH = Enhanced 
;     AU = Auto 
;    
;   Error Code description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     CK = Checksum Error 
;     GS = GroundShort Error 
;     P0 = IdParityBit0 Error 
;     P1 = IdParityBit1 Error 
;     IS = InconsistentSynch Error 
;     SR = SlaveNOtResponding Error 
;     SD = SlotDelay Error 
;     TO = Timeout Error 
;     VS = VBatShort Error 
;    
;   Columns decription: 
;   ~~~~~~~~~~~~~~~~~~~~ 
;   +Frame Number 
;   |           +Timestamp (microseconds) 
;   |           |           +Direction 
;   |           |           |    +Frame-ID (hex) 
;   |           |           |    |   +Frame Length 
;   |           |           |    |   |   +Data bytes (hex) 
;   |           |           |    |   |   |                       +Checksum 
;   |           |           |    |   |   |                       |   +Checksum Type 
;   |           |           |    |   |   |                       |   |     +Error Code 
;   |           |           |    |   |   |                       |   |     | 
;---+--   ------+-------  --+--  +-  +  -+ -- -- -- -- -- -- --  +-  +-  -+----------- 
     1)            11307   Pub   05  2  00 00                    7A  EH   
     2)            36305   Sub   02  2  -- --                    00  EH  SR/TO  
     3)            61305   Sub   07  8  -- -- -- -- -- -- -- --  00  EH  SR/TO 
     4)            86305   Pub   05  2  00 00                    7A  EH   
     5)           111304   Sub   02  2  -- --                    00  EH  SR/TO  
     6)           136303   Sub   07  8  C1 38 FE FF 3F F0 3E 6D  FC  EH  Ck 
     7)           161304   Pub   05  2  00 00                    7A  EH   
     8)           186302   Sub   02  2  FC 7F                    41  EH                 
```

### LIN Version 1.1

```text
;$FILEVERSION=1.1 
;$STARTTIME=40694.6971444676 
; 
;   C:\TraceFile.ltrc 
; 
;   Start time: 2011-05-31 16:43:53.282 
;    
;   Direction description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     Pub   = Publisher Frame 
;     Sub   = Subscriber Frame 
;     SubAL = Subscriber Auto Length Frame 
;    
;   Checksum Type description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     CL = Classic 
;     EH = Enhanced 
;     AU = Auto 
;    
;   Error Code description: 
;   ~~~~~~~~~~~~~~~~~~ 
;     CK = Checksum Error 
;     GS = GroundShort Error 
;     P0 = IdParityBit0 Error 
;     P1 = IdParityBit1 Error 
;     IS = InconsistentSynch Error 
;     SR = SlaveNOtResponding Error 
;     SD = SlotDelay Error 
;     TO = Timeout Error 
;     VS = VBatShort Error 
;    
;   Columns decription: 
;   ~~~~~~~~~~~~~~~~~~~~ 
;   +Frame Number 
;   |           +Timestamp (microseconds) 
;   |           |           +Direction 
;   |           |           |    +Frame-ID (hex) 
;   |           |           |    |   +Frame Length 
;   |           |           |    |   |   +Data bytes (hex) 
;   |           |           |    |   |   |                       +Checksum (hex) 
;   |           |           |    |   |   |                       |   +Checksum Type 
;   |           |           |    |   |   |                       |   |    +Error Code 
;   |           |           |    |   |   |                       |   |    | 
;---+--   ------+-------  --+--  +-  +  -+ -- -- -- -- -- -- --  +-  +-  -+----------- 
     1)           756186   Sub   02  2  -- --                    00  EH  SR/TO 
     2)           781185   Sub   01  8  -- -- -- -- -- -- -- --  00  EH  SR/TO 
     3)           806186   Pub   05  2  00 00                    7A  EH   
     4)           831184   Sub   02  2  -- --                    00  EH  SR/TO 
     5)           856183   Sub   01  8  C1 38 FE FF 3F F0 3E 6D  FC  EH  CK 
     6)           881183   Pub   05  2  00 00                    7A  EH   
     7)           906182   Sub   02  2  FC 7F                    41  EH  
     8)           931181   Sub   01  8  C1 38 FE FF 3F F0 E6 6A  C3  EH 
```
