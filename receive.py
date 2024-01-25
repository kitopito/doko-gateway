import serial
import time
import argparse
import hexdump
import datetime

import requests
   
workerURL = "https://dokosen-worker.kitopitowada.workers.dev/sensors"
# Use a service account

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("serial_port")
    parser.add_argument("-b", "--baud", default="9600")
    parser.add_argument("-m", "--model", default="E220-900JP")
    parser.add_argument("--rssi", action="store_true")

    args = parser.parse_args()

    return args

def checkData(payload_byte, dataNum):
    isEnoughLength = len(payload_byte) > 12

    isMine = payload_byte[0] == 0
    isIYH = payload_byte[2] == ord('i')
    isSTX = payload_byte[8] == ord('U')
    isData = payload_byte[10] == ord('d')
    isEnd = payload_byte[11 + 2 * dataNum] == ord('^')

    isValidData = isEnoughLength and isMine and isIYH and isSTX and isData and isEnd

    return isValidData

def processPayload(payload):
    payload_hex = payload.hex()

    message_length_hex = len(payload_hex) #メッセージを16進数で表現したときの長さ
    message_length = message_length_hex//2 #メッセージの長さ(バイト)
    #print("message length " + str(message_length_hex))

    header_length = 12
    bytesPerData = 2
    dataNum = int((message_length - header_length) / bytesPerData)
    #print("data num " + str(dataNum))

    payload_byte = list()
    for i in range(message_length):
        payload_byte.append(int(payload_hex[i * 2], 16) * 16 + int(payload_hex[i * 2 + 1], 16))
        #print(payload_byte[i])
    print(payload_byte)

    payload_log = ''
    for i in range(message_length_hex):
        payload_log += str(payload_hex[i])
    print(payload_log)


    isValidData = checkData(payload_byte, dataNum)
    print(isValidData)
    isValidDataInt = 0
    if isValidData:
        isValidDataInt = 1

    values = list()
    dataHead = 11
    if isValidData:
        for i in range(dataNum):
            # センサの測定値 = 1バイト目 * 256 + 2バイト目
            value = payload_byte[dataHead + i * 2] * 256 + payload_byte[dataHead + i * 2 + 1]
            values.append(value)
            print(value)

        deviceAddress = payload_byte[9]
        param = {"deviceAddress": deviceAddress, "value": values, "log": payload_log, isValidData: isValidDataInt}
        requests.post(workerURL, json = param)


def main():
    args = get_args()

    #if args.model == "E220-900JP":

    print("serial port:")
    print(args.serial_port)

    print("receive waiting...")
    with serial.Serial(args.serial_port, int(args.baud), timeout=None) as ser:
        payload = bytes()
        while True:
            if ser.in_waiting != 0:
                payload = payload + ser.read()

            elif ser.in_waiting == 0 and len(payload) != 0:
                time.sleep(0.030)

                if ser.in_waiting == 0:
                    t_now = datetime.datetime.now().time()
                    print(t_now.strftime('%H:%M:%S.%f') + "  recv data hex dump:")

                    if args.rssi:
                        rssi = int(payload[-1]) - 256
                        print(f"RSSI: {rssi} dBm")

                    str_d = hexdump.hexdump(payload, result='return')
                    print("RECEIVED\n")
                    print(str_d)
                    print("\n")

                    processPayload(payload)

                    payload = bytes()

    '''
    else:
        print("INVALID")
        return
    '''


if __name__ == "__main__":
    main()
