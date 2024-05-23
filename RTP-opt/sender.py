import sys
import socket
import math
from tokenize import Double
import time

from util import *


def sender(receiver_ip,receiver_port,window_size):
    """TODO: Open socket and send message from sys.stdin"""
    sorun_var_mi=False
    gelenler=[]
    window_base=0
    index_windows=0
    last_seq_num=0
    all_headers = []
    all_data=[]
    yanlis_window_base=0
    nerede_hata=0
    gonder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dinle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dinle.bind(('127.0.0.1',receiver_port+1))
    #49 byte packet_header boyutu sabit.
    #sender starts with a START message along with a random seq_num value,
    data=""
    pkt_start=makePacket(0,0,0,"")
    gonder.sendto(bytes(pkt_start),('127.0.0.1', receiver_port))
    #and wait for an ACK for this START message. 
    pkt_came, address = dinle.recvfrom(receiver_port+1)
    
    pkt_header=extractPacketHeader(pkt_came)
    for line in sys.stdin:#datalarin hepsini alma islemi.
        data+=line
    
    sinir=int(math.ceil(len(data) / 700))#toplam datanin uzunlugunu belirtmek icin
     
    if pkt_header.type==3:#baglanti kuruldu start mesaji icin ACK bilgisi alindi.
        for i in range(sinir):#datalari paketlere bolme islemi.her bir datanin lengthini 700 kullandim siniri asmamasi icin.
            if sinir==1:
                all_data.append(data);
                all_headers.append(PacketHeader(type=2, seq_num=i, length=len(data)))
                gelenler.append(0)
            else:
                all_data.append(data[700*i:700*(i+1)]);
                all_headers.append(PacketHeader(type=2, seq_num=i, length=len(data)))
                gelenler.append(0)
        print("Toplam "+str(sinir) +" Paket olusturuldu.")
        kontrol_paket=last_seq_num
        while(kontrol_paket<len(all_data)):
            t_end = time.time() + 0.5
            while time.time() < t_end and index_windows!=window_size and last_seq_num<len(all_data):#500 ms icinde bekle. windowdaki ack mesajlari icin bekle.       
                all_headers[last_seq_num].checksum = compute_checksum(all_headers[last_seq_num] / all_data[last_seq_num])
                pkt = all_headers[last_seq_num] / all_data[last_seq_num]
                gonder.sendto(bytes(pkt),('127.0.0.1', receiver_port))
                print(str(last_seq_num)+ ".Paket gonderildi")
                pkt_came2, address = dinle.recvfrom(receiver_port+1)                
                pkt_header2=extractPacketHeader(pkt_came2)#recevierin bir sonraki gonderdigi cumulative ack i bekliyor
                
                if pkt_header2.seq_num==last_seq_num:
                    gelenler[last_seq_num]=1#geldi demektir.
                    print(str(last_seq_num)+". paket icin ACK mesaji geldi.")
                
                index_windows+=1
                last_seq_num+=1
            
            index=window_base
            
            if(window_base+window_size<len(all_data)):
                window_base_kontrol=window_base+window_size
            else:
                window_base_kontrol=len(all_data)
            print("*********")
            while(index<window_base_kontrol):
                
                if(gelenler[index]==0):
                    sorun_var_mi=True
                    print("Window icindeki paketlerden Ack mesaji ulasmadi "+str(index))
                index+=1
            if(sorun_var_mi==True):#hata var windowdaki paketleri tekrar gonderme sadece hangi paket gitmemisse tekrar gonder.
                index1=window_base
                while(index1<window_base_kontrol) :
                    
                    if(gelenler[index1]==0):
                        all_headers[index1].checksum = compute_checksum(all_headers[index1] / all_data[index1])
                        pkt = all_headers[index1] / all_data[index1]
                        gonder.sendto(bytes(pkt),('127.0.0.1', receiver_port))
                        pkt_came2, address = dinle.recvfrom(receiver_port+1)                
                        pkt_header2=extractPacketHeader(pkt_came2)
                        if(pkt_header2.type==index1):
                            gelenler[index1]=1
                            index1+=1
                window_base+=window_size#shift
                index_windows=0    
                kontrol_paket=last_seq_num
                
                
            else:
                window_base+=window_size#shift
                index_windows=0    
                kontrol_paket=last_seq_num                 
                
            
            
        pkt_end= makePacket(1,last_seq_num+1,0,"")
        gonder.sendto(bytes(pkt_end),('127.0.0.1', receiver_port))     
    
        pkt_came3, address = dinle.recvfrom(receiver_port+1)                
        pkt_header3=extractPacketHeader(pkt_came3)
        if(pkt_header3.seq_num== last_seq_num+1):
            print("Baglanti sonlandi.")
    
        
        

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

def extractPacketHeader(pkt):
    pkt_header = PacketHeader(pkt[:16])
    # verify checksum
    msg = pkt[16:16+pkt_header.length]
    pkt_checksum = pkt_header.checksum
    pkt_header.checksum = 0
    computed_checksum = compute_checksum(pkt_header / msg)
    current_seq=pkt_header.seq_num;
    if pkt_checksum != computed_checksum:
        print("checksums not match")
        
    return pkt_header

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)
    

if __name__ == "__main__":
    main()
