from PUBGAPIConnect import PUBGAPI
import json
import numpy as np
import pandas as pd
from pandas import json_normalize

def Menu():
    select = -1
    print("배틀그라운드 API를 이용한 데이터 수집 툴")
    print("1.리더 보드 갱신")
    print("2.매칭정보 가져오기")
    print("3.매치 게임 요소 가져오기")
    print("4.매치 위치 정보 가져오기")
    print("5.매치 교전 정보 가져오기")
    select = int(input('====================> 입력 : '))
    return select

def Job(select):
    if(select==1):#리더보드 갱신
        dict_gamemode = {1:'solo',2:'duo',3:'squad'} #squad만 가능
        gamemode = dict_gamemode[int(input("\n=게임모드 입력=\n1.Solo\n2.Duo\n3.Squad ... "))]
        limitRank = int(input("검색할 최대 등수 ... ")) #등수제한(요청 리미트 때문에 양이 많을수록 이후 조회가 오래걸릴수 있음)
        PUBGAPI().LeaderBoard(gamemode,limitRank)
    elif(select==2):#매칭정보 갱신
        PUBGAPI().Match()
    elif(select==3):
        print("매치 게임 요소 가져오기")
        print("1.매치 자기장 정보")
        print("2.매치 비행기 정보")
        print("3.플레이어 착지지점")
        print("4.플레이어 이동경로")
        print("5.플레이어 교전 정보")
        print("6.플레이어 차량 탑승정보")
        print("7.플레이어 차량 하차정보")
        select = int(input('====================> 입력 : '))
        if(select==1):
            PUBGAPI().option("CirclePos").start()
        elif(select==2):
            PUBGAPI().option("AirPlanePos").start()
        elif(select==3):
            PUBGAPI().option("PlayerLanding").start()
        elif(select==4):
            PUBGAPI().option("PlayerPosition").start()
        elif(select==5):
            PUBGAPI().option("Attacker").start()
        elif(select==6):
            PUBGAPI().option("RideVehicle").start()
        elif(select==7):
            PUBGAPI().option("LeaveVehicle").start()
    elif(select==4):
        df = pd.read_json("Matches.json")
        print(df)
        

def main():
    while True:
        Choi = Menu()
        Job(Choi)

if __name__ == "__main__":
    main()