import serial
import time
import argparse
import hexdump
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import requests
   
workerURL = "https://dokosen-worker.kitopitowada.workers.dev/sensors"
# Use a service account
'''
cred = credentials.Certificate('dokosen-firebase-adminsdk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

status_number = 0
str_d = ''

num2Status = ["在室", "講義", "出張", "帰宅", "学内", "会議", ]
valueOfState = [
        [0x07DB, 0x081F, 0x0816], 
        [0x03DF, 0x0829, 0x0815], 
        [0x07BA, 0x0966, 0x0810], 
        [0x07F5, 0x0915, 0x07D6], 
        [0x07FC, 0x0828, 0x0584], 
        [0x07FE, 0x081D, 0x07F7], 
]
def value2State(value1, value2, value3):
    state = 0
    minError = 999999
    for i in range(6):
        error = (value1 - int(valueOfState[i][0])) ** 2 + (value2 - int(valueOfState[i][1])) ** 2 + (value3 - int(valueOfState[i][2])) ** 2
        if error < minError:
            minError = error
            state = i

    return state

def updateData(status_num):
    doc_ref = db.collection('teachers').document("0")
    doc_ref.update({
        "status": num2Status[status_num],
    })
'''


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("serial_port")
    parser.add_argument("-b", "--baud", default="9600")
    parser.add_argument("-m", "--model", default="E220-900JP")
    parser.add_argument("--rssi", action="store_true")

    args = parser.parse_args()

    return args


def main():
    global status_number
    args = get_args()

    if args.model == "E220-900JP":
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
                        str_d = hexdump.hexdump(payload, result='return')
                        if args.rssi:
                            rssi = int(payload[-1]) - 256
                            print(f"RSSI: {rssi} dBm")
                        print("RECEIVED\n")

                        print(str_d)
                        print("\n")
                        
                        #print(payload.hex())
                        payload_hex = payload.hex()
                        #k = payload_hex[0]*16 + payload_hex[1]
                        '''
                        first = int(payload_hex[0]) * 16 + int(payload_hex[1])
                        second = int(payload_hex[2], 16) * 16 + int(payload_hex[3], 16)
                        third = int(payload_hex[4], 16) * 16 + int(payload_hex[5], 16)
                        '''

                        message_length = len(payload_hex)
                        #print("message length " + str(message_length))
                        dataNum = int((message_length / 2 - 12) / 2)
                        #print("data num " + str(dataNum))

                        payload_byte = list()
                        for i in range(message_length//2):
                            payload_byte.append(int(payload_hex[i * 2], 16) * 16 + int(payload_hex[i * 2 + 1], 16))
                            #print(payload_byte[i])

                        payload_log = ''
                        for i in range(message_length):
                            payload_log += str(payload_hex[i])
                        print(payload_log)


                        isEnoughLength = len(payload_byte) > 12
                        isValidData = isEnoughLength;
                        if isEnoughLength:
                            isMine = payload_byte[0] == 0
                            isIYH = payload_byte[2] == ord('i')
                            isSTX = payload_byte[8] == ord('U')
                            isData = payload_byte[10] == ord('d')
                            isEnd = payload_byte[11 + 2 * dataNum] == ord('^')
                            isValidData = isMine and isIYH and isSTX and isData and isEnd
                        print(isValidData)
                        isValidDataNum = 0
                        if isValidData:
                            isValidDataNum = 1

                        values = list()
                        dataHead = 11
                        if isValidData:
                            #print('hoge')
                            for i in range(dataNum):
                                value = payload_byte[dataHead + i * 2] * 256 + payload_byte[dataHead + i * 2 + 1]
                                values.append(value)
                                print(value)
                            #value1 = int(payload_hex[3] * 256 + payload_hex[4])
                            #value2 = int(payload_hex[5] * 256 + payload_hex[6])
                            #value3 = int(payload_hex[7] * 256 + payload_hex[8])
                            #print(value[0])
                            #print(value[1])
                            #print(value[2])
                            '''
                            status_number_kari = value2State(value[0], value[1], value[2]) #int(str_d[-1])
                            print(status_number_kari)
                            if status_number != status_number_kari:
                                status_number = status_number_kari
                                updateData(status_number)
                            '''

                            deviceAddress = payload_byte[9]
                            j = {"deviceAddress": deviceAddress, "value": values, "log": payload_log, isValidData: isValidDataNum}
                            requests.post(workerURL, json = j)

                        payload = bytes()
    else:
        print("INVALID")
        return


if __name__ == "__main__":
    main()
