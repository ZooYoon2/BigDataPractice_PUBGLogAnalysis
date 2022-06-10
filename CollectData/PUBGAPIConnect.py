from lib2to3.pgen2.pgen import DFAState
import string, requests, json, numpy as np, pandas as pd
from pandas import json_normalize
import time
from chicken_dinner.pubgapi import PUBG
from chicken_dinner.constants import COLORS
from chicken_dinner.constants import map_dimensions
import os

def get_apikey(key_name, json_filename='secret.json'):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_filepath = os.path.join(BASE_DIR, json_filename)
    if not os.path.isfile(json_filepath):
        print('JSON File Not Found')
        raise FileNotFoundError
    with open(json_filepath) as (f):
        json_p = json.loads(f.read())
    try:
        value = json_p[key_name]
        return value
    except KeyError:
        error_msg = 'ERROR: Unvalid Key'
        return error_msg


class PUBGAPI:
    apikey: None
    header: None
    pubg: None

    def __init__(self):
        self.apikey = get_apikey('PUBGAPIKEY')
        self.header = {'Authorization ':'Bearer {}'.format(self.apikey),
         'Accept':'application/vnd.api+json'}
        self.pubg = PUBG((self.apikey), shard='kakao')

    def LeaderBoard(self, gameMode, limitRank):
        try:
            seasonId = 'division.bro.official.pc-2018-16'
            url_of_leaderBoard = 'https://api.pubg.com/shards/pc-kakao/leaderboards/{}/{}'.format(seasonId, gameMode)
            response = requests.get(url_of_leaderBoard, headers=(self.header))
            leaderBoard = response.json()
            del leaderBoard['data']
            del leaderBoard['links']
            del leaderBoard['meta']
            df = pd.json_normalize(leaderBoard['included'])
            df.columns = df.columns.str.split('.').str[(-1)]
            df = df.sort_values(by=['rank'])
            df = df.reset_index(drop=True)
            df = df.loc[1:limitRank]
            df.head(10)
            saveFile = input('저장할 제목을 입력하시오. : ')
            df.to_json(saveFile, orient='records')
            print('저장 완료')
        except requests.exceptions.HTTPError as e:
            try:
                print('API request Error Code : {}'.format(e))
            finally:
                e = None
                del e

    def Match(self,mapName):
        try:
            playerFile = input('플레이어 리스트 파일명을 입력하시오. : ')
            df_Player = pd.read_json(playerFile)
        except FileNotFoundError:
            print('플레이어 파일이 없습니다.')
            return
        else:
            df_Matches = pd.DataFrame()
            topcnt = df_Player['id'].count()
            pcnt = 0
            tocnt = 0
            for playerId in df_Player['id']:
                print('ID : {}'.format(playerId))
                url_of_matches = 'https://api.pubg.com/shards/kakao/players/{}'.format(playerId)
                response = requests.get(url_of_matches, headers=(self.header))
                while response.status_code != 200:
                    time.sleep(3)
                    response = requests.get(url_of_matches, headers=(self.header))

                matches = response.json()
                matches = matches['data']['relationships']['matches']['data']
                cnt = 0
                for match in matches:
                    try:
                        matchId = match['id']
                        cr_match = self.pubg.match(matchId)
                        matchJson = cr_match.data
                        if matchJson['attributes']['matchType'] != "competitive":
                            print('게임타입 경쟁전 외')
                            continue
                        if matchJson['attributes']['gameMode'] != "squad":
                            print('게임모드 스쿼드 외')
                            continue
                        if not (matchJson['attributes']['mapName'] in mapName):
                            print('맵 설정 외')
                            continue
                        del matchJson['relationships']
                        del matchJson['links']
                        df_temp = pd.json_normalize(matchJson)
                        df_temp.columns = df_temp.columns.str.split('.').str[(-1)]
                        df_Matches = pd.concat([df_Matches, df_temp])
                        cnt += 1
                        tocnt += 1
                    except requests.exceptions.HTTPError as e:
                        try:
                            print('API request Error Code : {}'.format(e))
                        finally:
                            e = None
                            del e

                    except KeyError as e:
                        try:
                            print('KeyError Error Code : {}'.format(e))
                        finally:
                            e = None
                            del e

                pcnt += 1
                print('{0}명 플레이어 중 {1}명 완료 // 추가된 매치 : {2} // 총 매치 : {3}'.format(topcnt, pcnt, cnt, tocnt))

            cnt_df_before = len(df_Matches)
            df_Matches = df_Matches.drop_duplicates()
            cnt_df_after = len(df_Matches)
            df_Matches = df_Matches.reset_index(drop=True)
            df_Matches.head(10)
            print('{}개의 매치중 중복 제거 {}개, 총 매치 갯수 {}', cnt_df_before, cnt_df_before - cnt_df_after, cnt_df_after)
            saveFile = input('저장할 제목을 입력하시오. : ')
            df_Matches.to_json(saveFile, orient='records')
            print('저장 완료')

    def player(self):
        try:
            playerFile = input('매치 파일명을 입력하시오. : ')
            df_Matches = pd.read_json(playerFile)
        except FileNotFoundError:
            print('매치 파일이 없습니다.')
            return
        cnt = 0
        tocnt = df_Matches['id'].count()
        df = pd.DataFrame({'playerName':object,  'avgRank':float,  'kda':float,  'damageDealt':float ,'dBNOs':float}, index=[0])
        for matchId in df_Matches['id']:
            try:
                cr_match = self.pubg.match(matchId)
                telemetry = cr_match.get_telemetry()
                players = telemetry.players()
                for name,id in players.items():
                    print(name,id)
                    #ID로부터 플레이어 정보 가져오기
                    seasonId = "division.bro.official.pc-2018-16"
                    url_of_playerInfo = 'https://api.pubg.com/shards/kakao/players/{}/seasons/{}/ranked'.format(id,seasonId)
                    response = requests.get(url_of_playerInfo, headers=(self.header))
                    if response.status_code == 404:
                            print("사용자 이름 변경 혹은 삭제로 인한 오류")
                            continue
                    while response.status_code != 200:
                        time.sleep(3)
                        response = requests.get(url_of_playerInfo, headers=(self.header))
                    playerInfo = response.json()
                    try:
                        playerInfo = playerInfo['data']['attributes']['rankedGameModeStats']["squad"]
                        df = df.append({'playerName':name, 'avgRank':playerInfo['avgRank'],  'kda':playerInfo['kda'],
                                              'damageDealt':playerInfo['damageDealt'],'dBNOs':playerInfo['dBNOs']}, ignore_index=True)
                    except KeyError as e:
                        print(e,"기록 없음")     
                cnt += 1
                print('총 {} 개 매치 중 {} 개 완료'.format(tocnt, cnt))
            except requests.exceptions.HTTPError as e:
                try:
                    print('API request Error Code : {}'.format(e))
                finally:
                    e = None
                    del e
            except KeyError as e:
                try:
                    print('KeyError Error Code : {}'.format(e))
                finally:
                    e = None
                    del e
            #except:
                #print('Other Error')
                #ecnt += 1
        df = df.drop_duplicates()
        df = df.reset_index(drop=True)
        df.head(10)
        saveFile = input('저장할 제목을 입력하시오. : ')
        result = df.to_json(saveFile, orient='records')
        print('저장 완료')

    def option(self, func: string):
        if func.lower() in ('circlepos', 'circleposition'):
            return self.func(self.MatchesCircle)
        if func.lower() in ('airplaneroute', 'airplanepos', 'airplaneposition'):
            return self.func(self.MatchesAirPlaneRoute)
        if func.lower() in ('playerposition', 'playerpos'):
            return self.func(self.MatchesPlayerPosition)
        if func.lower() in ('playerlanding', 'playerlandposition'):
            return self.func(self.MatchesPlayerLanding)
        if func.lower() in ('playerdamages', 'attacker', 'damageposition'):
            return self.func(self.MatchesPlayerDamages)
        if func.lower() in ('ridevehiclelog', 'ridevehicle'):
            return self.func(self.MatchesVehicleRide)
        if func.lower() in ('leavevehiclelog', 'leavevehicle'):
            return self.func(self.MatchesVehicleLeave)
        raise Exception('잘못된 키워드')

    def MatchesCircle(self, matchId):
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        circlePos = telemetry.circle_positions()
        header = {'matchId': matchId}
        header.update(circlePos)
        df = pd.json_normalize(header)
        return df

    def MatchesAirPlaneRoute(self, matchId):
        df = pd.DataFrame({'matchId':object,  'mapX':float,  'slope':float,  'intercept':float}, index=[0])
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        positions = telemetry.player_positions()
        playerName = telemetry.player_names()[0]
        standardPlayerPos = np.array(positions[playerName])
        mapX, mapY = map_dimensions[telemetry.map_id()]
        standardPlayerPos[:, 2] = mapY - standardPlayerPos[:, 2]
        slope = (standardPlayerPos[0][2] - standardPlayerPos[1][2]) / (standardPlayerPos[0][1] - standardPlayerPos[1][1])
        intercept = standardPlayerPos[1][2] - standardPlayerPos[1][1] * slope
        airplaneX = np.linspace(0, mapX, 100)
        airplaneY = slope * airplaneX + intercept
        airplaneX = np.delete(airplaneX, np.where(airplaneY > mapY))
        airplaneY = np.delete(airplaneY, np.where(airplaneY > mapY))
        df = df.append({'matchId':matchId,  'mapX':mapX,  'slope':slope,  'intercept':intercept}, ignore_index=True)
        return df

    def MatchesPlayerPosition(self, matchId):
        df = pd.DataFrame({'matchId':object,  'playerName':object,  'ranking':int,  'position':object}, index=[0])
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        position = telemetry.player_positions()
        ranking = telemetry.rankings()
        for rank in ranking:
            roster = ranking[rank]
            for player in roster:
                df = df.append({'matchId':matchId,  'playerName':player,  'ranking':rank,  'position':position[player]}, ignore_index=True)

        return df

    def MatchesPlayerLanding(self, matchId):
        df = pd.DataFrame({'matchId':object,  'playerName':object,  'ranking':int,  'x':float,  'y':float}, index=[0])
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        ranking = telemetry.rankings()
        unequips = telemetry.filter_by('log_item_unequip')
        landing_locations = {unequip['character']['name']:(unequip['character']['location']['x'], unequip['character']['location']['y'], unequip['character']['team_id']) for unequip in unequips if unequip['item']['item_id'] == 'Item_Back_B_01_StartParachutePack_C' if unequip['item']['item_id'] == 'Item_Back_B_01_StartParachutePack_C'}
        landing_locations = pd.DataFrame(landing_locations).T.reset_index()
        landing_locations.columns = ['name', 'x', 'y', 'teamId']
        for rank in ranking:
            roster = ranking[rank]
            for player in roster:
                landing = landing_locations[(landing_locations['name'] == player)]
                df = df.append({'matchId':matchId,  'playerName':player,  'ranking':rank,  'x':landing.x,  'y':landing.y}, ignore_index=True)

        return df

    def MatchesPlayerDamages(self, matchId):
        df = pd.DataFrame({'matchId':object,  'attacker':object,  'time':object,  'a_x':float,  'a_y':float,  'a_z':float,  'v_x':float,
         'v_y':float,  'v_z':float},
          index=[0])
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        ranking = telemetry.rankings()
        damages = telemetry.player_damages()
        for attacker in damages.keys():
            for damage in damages[attacker]:
                df = df.append({'matchId':matchId,  'attacker':attacker,  'time':damage[0],  'a_x':damage[1],  'a_y':damage[2],  'a_z':damage[3],
                 'v_x':damage[4],  'v_y':damage[5],  'v_z':damage[6]},
                  ignore_index=True)

        return df

    def MatchesVehicleRide(self, matchId):
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        vehicles = telemetry.filter_by('log_vehicle_ride')
        df = pd.DataFrame({'matchId':object,  'player':object,  'time':object,  'x':float,  'y':float,  'z':float}, index=[
         0])
        for log in vehicles:
            if log['vehicle']['vehicle_type'] == 'WheeledVehicle':
                df = df.append({'matchId':matchId,  'player':log['character']['name'],  'time':log.timestamp,  'x':log['character']['location']['x'],
                 'y':log['character']['location']['y'],  'z':log['character']['location']['z']},
                  ignore_index=True)

        return df

    def MatchesVehicleLeave(self, matchId):
        cr_match = self.pubg.match(matchId)
        telemetry = cr_match.get_telemetry()
        vehicles = telemetry.filter_by('log_vehicle_leave')
        df = pd.DataFrame({'matchId':object,  'player':object,  'time':object,  'x':float,  'y':float,  'z':float}, index=[
         0])
        for log in vehicles:
            if log['vehicle']['vehicle_type'] == 'WheeledVehicle':
                df = df.append({'matchId':matchId,  'player':log['character']['name'],  'time':log.timestamp,  'x':log['character']['location']['x'],
                 'y':log['character']['location']['y'],  'z':log['character']['location']['z']},
                  ignore_index=True)

        return df

    class func:
        newFunction: None

        def __init__(self, fuction):
            self.newFunction = fuction

        def start(self):
            try:
                matchesFile = input('매치경기 리스트 파일명을 입력하시오. : ')
                df_Matches = pd.read_json(matchesFile)
            except FileNotFoundError:
                print('플레이어 파일이 없습니다.')
                return
            else:
                cnt = 0
                ecnt = 0
                tocnt = df_Matches['id'].count()
                df_main = pd.DataFrame()
                b_first = True
                for matchId in df_Matches['id']:
                    try:
                        df_matchInfo = self.newFunction(matchId)
                        if b_first:
                            df_main = df_matchInfo
                            b_first = False
                        else:
                            df_main = pd.concat([df_matchInfo, df_main])
                        cnt += 1
                        print('총 {} 개 매치 중 {} 개 완료 (성공 {}개, 오류 {}개)'.format(tocnt, cnt + ecnt, cnt, ecnt))
                    except requests.exceptions.HTTPError as e:
                        try:
                            print('API request Error Code : {}'.format(e))
                            ecnt += 1
                        finally:
                            e = None
                            del e

                    except KeyError as e:
                        try:
                            print('KeyError Error Code : {}'.format(e))
                            ecnt += 1
                        finally:
                            e = None
                            del e

                    except:
                        print('Other Error')
                        ecnt += 1

                df_main = df_main.reset_index(drop=True)
                df_main.head(10)
                saveFile = input('저장할 제목을 입력하시오. : ')
                result = df_main.to_json(saveFile, orient='records')
                print('저장 완료')