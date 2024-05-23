import sys
import socket

from util import *

baglanti_durumunda=False;



def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    dinle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gonder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dinle.bind(('127.0.0.1',receiver_port))
    hata_var=0
    cumulative_ack=0
    gelen_paketler=[]
    window_base=0
    window_index=0
    while True:
        # receive packet
        pkt, address = dinle.recvfrom(receiver_port)
        
        # extract header and payload
        #python sender.py 127.0.0.01 1234 4  < deneme.txt
            
        # verify checksum
        pkt_header=extractPacketHeader(pkt)
        if(pkt_header.__eq__("checksum not match")):#not send back ack
           continue
        data=extractData(pkt)
        if pkt_header.type==1:
            packet=makePacket(3,pkt_header.seq_num,0,"")
            gonder.sendto(bytes(packet),('127.0.0.1', receiver_port+1))
            #print("Connection bitti.")
            break
        
        if pkt_header.type == 2:
            if(pkt_header.seq_num<cumulative_ack):
                msg=str(data)
                msg=msg[2:len(msg)-1]
                gelen_paketler[pkt_header.seq_num]=msg
                pkt=makePacket(3,pkt_header.seq_num,0,"")
                gonder.sendto(bytes(pkt),('127.0.0.1', receiver_port+1))
                continue
            elif(pkt_header.seq_num==cumulative_ack) :    
                gelen_paketler.insert(cumulative_ack,"")
            if cumulative_ack==pkt_header.seq_num:#yani N e sitse. En buyuk olandan +1 fazlasini gonder.
                window_index+=1
                if(window_index==window_size):
                    window_index=0
                    window_base+=window_size    
                msg=str(data)
                msg=msg[2:len(msg)-1]
                gelen_paketler[cumulative_ack]=msg                
                pkt=makePacket(3,cumulative_ack,0,"")
                gonder.sendto(bytes(pkt),('127.0.0.1', receiver_port+1)) #bekledigi paketi gondericek.                 
                cumulative_ack+=1
            else:#burada da datayi alicak.
                
                pkt=makePacket(3,cumulative_ack,0,"") 
                msg=str(data)
                msg=msg[2:len(msg)-1]#gelen paketi dogru sekilde duzenliyor.     
                gelen_paketler[cumulative_ack]=""    
                gonder.sendto(bytes(pkt),('127.0.0.1', receiver_port+1))     
                cumulative_ack+=1        
                
        # print payload
        if pkt_header.type == 0:
            
            packet=makePacket(3,pkt_header.seq_num,0,"")
            gonder.sendto(bytes(packet),('127.0.0.1', receiver_port+1))

    
    #print(len(gelen_paketler))
    #for i in range (len(gelen_paketler)):
        #print(gelen_paketler[i])
    
    for i in range(len(gelen_paketler)):
        sys.stdout.write(gelen_paketler[i])
    sys.stdout.close()     

def makePacket(type,seq,length,data):
    pkt=""
    if type==0:
        pkt_header = PacketHeader(type=0, seq_num=seq, length=0)
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        return pkt
    elif type==1:
        pkt_header = PacketHeader(type=1, seq_num=seq, length=0)
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        return pkt
    elif type==2:
        pkt_header = PacketHeader(type=2, seq_num=seq, length=len(data))
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        return pkt
    elif type==3:
        pkt_header = PacketHeader(type=3, seq_num=seq, length=0)
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        return pkt
    
    return pkt
def extractData(pkt):
    pkt_header=extractPacketHeader(pkt)
    msg = pkt[16:16+pkt_header.length]
    return msg
    

def extractPacketHeader(pkt):
    pkt_header = PacketHeader(pkt[:16])
    # verify checksum
    msg = pkt[16:16+pkt_header.length]
    pkt_checksum = pkt_header.checksum
    pkt_header.checksum = 0
    computed_checksum = compute_checksum(pkt_header / msg)
    if pkt_checksum != computed_checksum:
        return "checksums not match"
        
    return pkt_header


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)
    

if __name__ == "__main__":
    main()
