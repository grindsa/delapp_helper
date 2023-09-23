# -*- coding: utf-8 -*-
""" delapphelper """
import sys
import os
from datetime import datetime
import requests
import urllib3
import logging
import configparser

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def config_load(logger=None, mfilter=None, cfg_file='hockeygraphs.cfg'):
    """ small configparser wrappter to load a config file """
    if logger:
        logger.debug('config_load({1}:{0})'.format(mfilter, cfg_file))
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(cfg_file)
    return config

def print_debug(debug, text):
    """ little helper to print debug messages """
    if debug:
        print('{0}: {1}'.format(datetime.now(), text))

def logger_setup(debug):
    """ setup logger """
    if debug:
        log_mode = logging.DEBUG
    else:
        log_mode = logging.INFO

    # log_formet = '%(message)s'
    log_format = '%(asctime)s - hockey_graphs - %(levelname)s - %(message)s'
    logging.basicConfig(
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_mode)
    logger = logging.getLogger('hockey_graph')
    return logger

class DelAppHelper():
    """ main class to access the PA REST API """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    debug = None
    os_ = 'android'
    logger = None
    deviceid = None
    tournamentid = None
    base_url = None
    pennydel_url = None
    mobile_api = None
    del_api = None
    shift_name = None

    def __init__(self, debug=False, deviceid='bada55bada55666'):
        self.debug = debug
        self.deviceid = deviceid
        self.logger = logger_setup(debug)

    def __enter__(self):
        """ Makes Stirpahelper a Context Manager
        with DelAppHelper(....) as del_app_helper:
            print (...) """
        self._config_load()
        return self

    def __exit__(self, *args):
        """ Close the connection at the end of the context """
        # self.logout()
        pass


    def _config_load(self):
        """" load config from file """
        self.logger.debug('_config_load()')
        config_dic = config_load(cfg_file=os.path.dirname(__file__)+'/'+'delapphelper.cfg')
        if 'Urls' in config_dic:
            if 'base_url' in config_dic['Urls']:
                self.base_url = config_dic['Urls']['base_url']
            if 'pennydel_url' in config_dic['Urls']:
                self.pennydel_url = config_dic['Urls']['pennydel_url']
            if 'mobile_api' in config_dic['Urls']:
                self.mobile_api = config_dic['Urls']['mobile_api']
            if 'del_api' in config_dic['Urls']:
                self.del_api = config_dic['Urls']['del_api']
            if 'Shifts' in config_dic and 'shift_name' in config_dic['Shifts']:
                self.shift_name = config_dic['Shifts']['shift_name']

        self.logger.debug('_config_load() ended.')

    def api_post(self, url, data):
        """ generic wrapper for an API post call """
        self.logger.debug('DelAppHelper.api_post()\n')
        data['os'] = self.os_
        api_response = requests.post(url=url, data=data, headers=self.headers, verify=False)
        if api_response.ok:
            json_dic = api_response.json()
            return json_dic
        else:
            print(api_response.raise_for_status())
            return None

    def gamesituations_get(self, game_id):
        """ get game situations """
        self.logger.debug('DelAppHelper.gamesituations_get({0})\n'.format(game_id))
        data = {'requestName': 'gameSituations',
                'gameNumber': game_id,
                'tournamentId': self.tournamentid,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def gamesituations_extended_get(self, tournament_id, game_id):
        """ get game situations """
        self.logger.debug('DelAppHelper.gamesituations_get({0})\n'.format(game_id))
        data = {'requestName': 'gameSituationsExtended',
                'gameNumber': game_id,
                'tournamentId': tournament_id,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def game_filter(self, date_, team):
        """ filter match based on time and team name """
        self.logger.debug('DelAppHelper.match_filter({0}, {1})\n'.format(date_, team))
        game_dic = self.games_get()

        game_details = {}
        for game in game_dic:
            if game['dateTime'] == date_:
                if team in (game['guestTeam'], game['homeTeam']):
                    game_details = game
                    break

        return game_details

    def gameheader_get(self, match_id):
        """ get periodevents from del.org """
        self.logger.debug('DelAppHelper.gameheader_get({0})\n'.format(match_id))

        url = '{0}/matches/{1}/game-header.json'.format(self.del_api, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def gameresult_get(self, game_id):
        """ get games """
        self.logger.debug('DelAppHelper.gameresult_get()\n')
        data = {'requestName': 'gameResults',
                'gameNumber': game_id,
                'tournamentId': self.tournamentid,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def gameschedule_get(self, year, league_id, team_id):
        """ get season schedule for a single team """
        self.logger.debug('DelAppHelper.gameschedule_get({0}:{1}:{2})\n'.format(year, league_id, team_id))
        url = '{0}/league-team-matches/{1}/{2}/{3}.json'.format(self.del_api, year, league_id, team_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def games_get(self, tournamentid=None):
        """ get games """
        self.logger.debug('DelAppHelper.games_get({0}) via mobile_api\n'.format(tournamentid))

        if not tournamentid:
            tournamentid = self.tournamentid

        data = {'requestName': 'games',
                'deviceId': self.deviceid,
                'tournamentId': tournamentid,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def fairplay_ranking_get(self, year, league_id):
        self.logger.debug('DelAppHelper.fairplay_ranking_get({0}:{1})\n'.format(year, league_id))
        url = '{0}/fair-play/{1}/{2}.json'.format(self.del_api, year, league_id)
        print(url)
        return requests.get(url, headers=self.headers, verify=False).json()

    def faceoffs_get(self, match_id):
        """ get faceoffs per match """
        self.logger.debug('DelAppHelper.faceoffs_get({0})\n'.format(match_id))
        url = '{0}/matches/{1}/faceoffs.json'.format(self.del_api, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def lineup_get(self, game_id):
        """ get lineup """
        self.logger.debug('DelAppHelper.linup_get()\n')
        url = '{0}/matches/{1}/roster.json'.format(self.del_api, game_id)

        return requests.get(url, headers=self.headers, verify=False).json()

    def lineup_dict(self, game_id, home_match):
        """ get lineup """
        self.logger.debug('DelAppHelper.linup_get()\n')

        # Positions
        # 3 - leftwing
        # 4 - center
        # 5 - rigtwing
        # 1 - rdefense
        # 2 - defense

        result = self.lineup_get(game_id)
        lineup_dic = {}

        if home_match:
            prim_key = 'home'
        else:
            prim_key = 'visitor'

        for player_id, player_data in result[prim_key].items():
            role = int(str(player_id)[0])
            line_number = int(str(player_id)[1])
            position = int(str(player_id)[2])
            if line_number not in lineup_dic:
                lineup_dic[line_number] = {}


            lineup_dic[line_number][int('{0}{1}'.format(role, position))] = '{0} {1} ({2})'.format(player_data['name'], player_data['surname'], player_data['jersey'])

        return (lineup_dic, result)

    def line_get(self, line_dic, headline):
        """ line get """
        self.logger.debug('DelAppHelper.line_get()\n')
        line = '*{0}*\n'.format(headline)

        if 11 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[11])
        if 12 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[12])
        if 32 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[32])
        if 31 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[31])
        if 33 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[33])
        if 21 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[21])
        if 22 in line_dic:
            line = '{0}{1}\n'.format(line, line_dic[22])
        return line

    def lineup_format(self, game_id, home_match, match_id):
        """ get format """
        self.logger.debug('DelAppHelper.linup_format()\n')
        (lineup_dic, raw_json) = self.lineup_dict(game_id, home_match)

        lineup = ''
        data_dic = {}
        if 0 in lineup_dic:
            if lineup_dic[0]:
                line = self.line_get(lineup_dic[0], 'Goalies')
                lineup = '{0}{1}\n'.format(lineup, line)
        if 1 in lineup_dic:
            if lineup_dic[1]:
                line = self.line_get(lineup_dic[1], '1. Reihe')
                lineup = '{0}{1}\n'.format(lineup, line)
                data_dic['r1'] = line
        if 2 in lineup_dic:
            if lineup_dic[2]:
                line = self.line_get(lineup_dic[2], '2. Reihe')
                lineup = '{0}{1}\n'.format(lineup, line)
                data_dic['r2'] = line
        if 3 in lineup_dic:
            if lineup_dic[3]:
                line = self.line_get(lineup_dic[3], '3. Reihe')
                lineup = '{0}{1}\n'.format(lineup, line)
                data_dic['r3'] = line
        if 4 in lineup_dic:
            if lineup_dic[4]:
                line = self.line_get(lineup_dic[4], '4. Reihe')
                lineup = '{0}{1}\n'.format(lineup, line)
                data_dic['r4'] = line
        if 5 in lineup_dic:
            if lineup_dic[5]:
                line = self.line_get(lineup_dic[5], '5. Reihe')
                lineup = '{0}{1}\n'.format(lineup, line)
                data_dic['r5'] = line

        return lineup, raw_json

    def myteam_get(self, team):
        """ get games """
        self.logger.debug('DelAppHelper.myteam_get({0})\n'.format(team))
        data = {'requestName': 'myTeam',
                'deviceId': self.deviceid,
                'tournamentId': self.tournamentid,
                'noc': team,
                'lastUpdate': 1}
        return self.api_post(self.mobile_api, data)

    def periodevents_get(self, match_id):
        """ get periodevents from del.org """
        self.logger.debug('DelAppHelper.periodevents_get({0}) from del.org\n'.format(match_id))

        url = '{0}/matches/{1}/period-events.json'.format(self.del_api, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def playerstats_get(self, match_id, team_id):
        """ get playerstats_get from del.org """
        self.logger.debug('DelAppHelper.playerstats_get({0}:{1})\n'.format(match_id, team_id))
        url = '{0}/matches/{1}/team-stats/{2}.json'.format(self.del_api, match_id, team_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def playofftree_get(self, year_, league_id=3):
        """ get playoff tree """
        self.logger.debug('DelAppHelper.playofftree_get({0}:{1})\n'.format(year_, league_id))
        url = '{0}/league-playoffs/{1}/{2}.json'.format(self.del_api, year_, league_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def reflist_get(self, game_id):
        """ get refs """
        self.logger.debug('DelAppHelper.reflist_get()\n')

        game_header = self.gameheader_get(game_id)

        if 'referees' in game_header:
            ref_dic = game_header['referees']
        else:
            ref_dic = {}

        ref_list = []
        if 'headReferee1' in ref_dic:
            ref_list.append(ref_dic['headReferee1']['name'])
        if 'headReferee2' in ref_dic:
            ref_list.append(ref_dic['headReferee2']['name'])
        if 'lineReferee1' in ref_dic:
            ref_list.append(ref_dic['lineReferee1']['name'])
        if 'lineReferee2' in ref_dic:
            ref_list.append(ref_dic['lineReferee2']['name'])

        return (ref_list, ref_dic)

    def roster_get(self, match_id):
        """ get match statistics per player """
        self.logger.debug('DelAppHelper.roster_get({0}) from del.org\n'.format(match_id))
        url = '{0}/matches/{1}/roster.json'.format(self.del_api, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def scorers_get(self, match_id):
        """ get match statistics per player """
        self.logger.debug('DelAppHelper.scorers_get({0})\n'.format(match_id))
        url = '{0}/matches/{1}/top-scorers.json'.format(self.base_url, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def shifts_get(self, match_id):
        """ get shifts from DEL api """
        self.logger.debug('DelAppHelper.shifts_get({0})\n'.format(match_id))
        url = '{0}/matches/{1}/{2}'.format(self.del_api, match_id, self.shift_name)
        return requests.get(url, headers=self.headers, verify=False).json()

    def shots_get(self, match_id):
        """ get shots from api """
        self.logger.debug('DelAppHelper.periodevents_get({0})\n'.format(match_id))
        url = '{0}/visualization/shots/{1}.json'.format(self.del_api, match_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def standings_get(self, table_id=27):
        """ get standings for a certain season"""
        url = '{0}/tables/{1}.json'.format(self.del_api, table_id)
        print(url)
        return requests.get(url, headers=self.headers, verify=False).json()

    def teamplayers_get(self, season_name, team_id=3, league_id=1):
        """ get playerinformation per team via rest """
        # 1 - for DEL Regular season
        # 3 - for DEL Playoffs
        # 4 - for Magenta Cup
        self.logger.debug('DelAppHelper.teamplayers_get({0}:{1})\n'.format(season_name, team_id))
        url = '{0}/league-team-stats/{1}/{2}/{3}.json'.format(self.del_api, season_name, league_id, team_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def teammatches_get(self, season_name, team_id=3, league_id=1):
        """ get matches for a certain team league_id - 1 regular, 3 playoff """
        self.logger.debug('DelAppHelper.teammatches_get({0}:{1}:{2})\n'.format(season_name, team_id, league_id))
        url = '{0}/league-team-matches/{1}/{2}/{3}.json'.format(self.del_api, season_name, league_id, team_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def teammembers_get(self, team_name):
        """ get data from all players of a team """
        self.logger.debug('DelAppHelper.teammembers_get({0})\n'.format(team_name))
        data = {'requestName': 'teamMembers',
                'tournamentId': 68, # self.tournamentid,
                'noc': team_name,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def teamstats_get(self, match_id, team_id):
        """ get teamstats_get from del.org """
        self.logger.debug('DelAppHelper.teamstats_get({0}:{1})\n'.format(match_id, team_id))
        url = '{0}/matches/{1}/team-stats/{2}.json'.format(self.del_api, match_id, team_id)
        return requests.get(url, headers=self.headers, verify=False).json()

    def teamstatssummary_get(self, delseason, leagueid, team_id):
        """ get teamstats_get from del.org """
        self.logger.debug('DelAppHelper.teamstatssummary_get({0}:{1}:{2})\n'.format(delseason, leagueid, team_id))
        url = '{0}/league-all-team-stats/{1}/{2}/{3}.json'.format(self.del_api, delseason, leagueid, team_id)
        print(url)
        return requests.get(url, headers=self.headers, verify=False).json()

    def teamstandings_get(self):
        """ get games """
        self.logger.debug('DelAppHelper.teamStandings_get()\n')
        data = {'requestName': 'teamStandings',
                'tournamentId': self.tournamentid,
                'lastUpdate': 0}
        return self.api_post(self.mobile_api, data)

    def tournamentid_get(self):
        """ get tournament id """
        self.logger.debug('DelAppHelper.tournamentid_get() via mobile_api\n')
        data = {'requestName': 'tournamentList', 'lastUpdate': 0}
        result = self.api_post(self.mobile_api, data)
        if result:
            if 'tournamentID' in result[-1]:
                self.logger.debug('DelAppHelper.tournamentid_get() set tournament to: {0}\n'.format(result[-1]['tournamentID']))
                self.tournamentid = result[-1]['tournamentID']
        self.logger.debug('DelAppHelper.tournamentid_get() ended with: {}\n'.format(self.tournamentid))
        return result
