# -*- coding: utf-8 -*-
""" delapphelper """
import os
from datetime import datetime
import logging
import configparser
import requests


def config_load(logger=None, cfg_file='delapp_helper.cfg'):
    """ small configparser wrappter to load a config file """
    if logger:
        logger.debug(f'config_load({cfg_file})')
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(cfg_file)
    return config


def print_debug(debug, text):
    """ little helper to print debug messages """
    if debug:
        print(f'{datetime.now()}: {text}')


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
    timeout = 20

    def __init__(self, debug=False, cfg_file=os.path.dirname(__file__) + '/' + 'delapphelper.cfg', deviceid='bada55bada55666'):
        self.debug = debug
        self.deviceid = deviceid
        self.logger = logger_setup(debug)
        self.cfg_file = cfg_file

    def __enter__(self):
        """ Makes Stirpahelper a Context Manager
        with DelAppHelper(....) as del_app_helper:
            print (...) """
        self._config_load()
        return self

    def __exit__(self, *args):
        """ Close the connection at the end of the context """

    def _config_load(self):
        """" load config from file """
        self.logger.debug('_config_load()')
        config_dic = config_load(logger=self.logger, cfg_file=self.cfg_file)
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
        api_response = requests.post(url=url, data=data, headers=self.headers, timeout=self.timeout, verify=False)
        if api_response.ok:
            result = api_response.json()
        else:
            print(api_response.raise_for_status())
            result = None
        return result

    def gameheader_get(self, match_id):
        """ get periodevents from del.org """
        self.logger.debug('DelAppHelper.gameheader_get(%s)\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/game-header.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def gameschedule_get(self, year, league_id, team_id):
        """ get season schedule for a single team """
        self.logger.debug('DelAppHelper.gameschedule_get(%s:%s:%s)\n', year, league_id, team_id)
        url = f'{self.del_api}/league-team-matches/{year}/{league_id}/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def fairplay_ranking_get(self, year, league_id):
        """ get fairplay ranking """
        self.logger.debug('DelAppHelper.fairplay_ranking_get(%s:%s)\n', year, league_id)
        url = f'{self.del_api}/fair-play/{year}/{league_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def faceoffs_get(self, match_id):
        """ get faceoffs per match """
        self.logger.debug('DelAppHelper.faceoffs_get(%s)\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/faceoffs.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def lineup_get(self, game_id):
        """ get lineup """
        self.logger.debug('DelAppHelper.linup_get()\n')
        url = f'{self.del_api}/matches/{game_id}/roster.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

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

        if prim_key in result and result[prim_key]:
            for player_id, player_data in result[prim_key].items():
                role = int(str(player_id)[0])
                line_number = int(str(player_id)[1])
                position = int(str(player_id)[2])
                if line_number not in lineup_dic:
                    lineup_dic[line_number] = {}
                lineup_dic[line_number][int(f'{role}{position}')] = f'{player_data["name"]} {player_data["surname"]} ({player_data["jersey"]})'

        return (lineup_dic, result)

    def _line_get(self, line_dic, headline):
        """ line get """
        self.logger.debug('DelAppHelper._line_get()\n')
        line = f'*{headline}*\n'

        if 11 in line_dic:
            line = f'{line}{line_dic[11]}\n'
        if 12 in line_dic:
            line = f'{line}{line_dic[12]}\n'
        if 32 in line_dic:
            line = f'{line}{line_dic[32]}\n'
        if 31 in line_dic:
            line = f'{line}{line_dic[31]}\n'
        if 33 in line_dic:
            line = f'{line}{line_dic[33]}\n'
        if 21 in line_dic:
            line = f'{line}{line_dic[21]}\n'
        if 22 in line_dic:
            line = f'{line}{line_dic[22]}\n'
        return line

    def lineup_format(self, game_id=None, home_match=True):
        """ get format """
        self.logger.debug('DelAppHelper.linup_format()\n')
        (lineup_dic, raw_json) = self.lineup_dict(game_id, home_match)

        lineup = ''
        data_dic = {}
        if 0 in lineup_dic:
            if lineup_dic[0]:
                line = self._line_get(lineup_dic[0], 'Goalies')
                lineup = f'{lineup}{line}\n'
        if 1 in lineup_dic:
            if lineup_dic[1]:
                line = self._line_get(lineup_dic[1], '1. Reihe')
                lineup = f'{lineup}{line}\n'
                data_dic['r1'] = line
        if 2 in lineup_dic:
            if lineup_dic[2]:
                line = self._line_get(lineup_dic[2], '2. Reihe')
                lineup = f'{lineup}{line}\n'
                data_dic['r2'] = line
        if 3 in lineup_dic:
            if lineup_dic[3]:
                line = self._line_get(lineup_dic[3], '3. Reihe')
                lineup = f'{lineup}{line}\n'
                data_dic['r3'] = line
        if 4 in lineup_dic:
            if lineup_dic[4]:
                line = self._line_get(lineup_dic[4], '4. Reihe')
                lineup = f'{lineup}{line}\n'
                data_dic['r4'] = line
        if 5 in lineup_dic:
            if lineup_dic[5]:
                line = self._line_get(lineup_dic[5], '5. Reihe')
                lineup = f'{lineup}{line}\n'
                data_dic['r5'] = line

        return lineup, raw_json

    def periodevents_get(self, match_id):
        """ get periodevents from del.org """
        self.logger.debug('DelAppHelper.periodevents_get(%s) from del.org\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/period-events.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def playerstats_get(self, match_id, team_id):
        """ get playerstats_get from del.org """
        self.logger.debug('DelAppHelper.playerstats_get(%s:%s)\n', match_id, team_id)
        url = f'{self.del_api}/matches/{match_id}/team-stats/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def playofftree_get(self, year_, league_id=3):
        """ get playoff tree """
        self.logger.debug('DelAppHelper.playofftree_get(%s:%s)\n', year_, league_id)
        url = f'{self.del_api}/league-playoffs/{year_}/{league_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

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
        self.logger.debug('DelAppHelper.roster_get(%s) from del.org\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/roster.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def scorers_get(self, match_id):
        """ get match statistics per player """
        self.logger.debug('DelAppHelper.scorers_get(%s)\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/top-scorers.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def shifts_get(self, match_id):
        """ get shifts from DEL api """
        self.logger.debug('DelAppHelper.shifts_get(%s)\n', match_id)
        url = f'{self.del_api}/matches/{match_id}/{self.shift_name}'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def shots_get(self, match_id):
        """ get shots from api """
        self.logger.debug('DelAppHelper.periodevents_get(%s)\n', match_id)
        url = f'{self.del_api}/visualization/shots/{match_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def standings_get(self, table_id=27):
        """ get standings for a certain season"""
        self.logger.debug('DelAppHelper.standings_get(%s)\n', table_id)
        url = f'{self.del_api}/tables/{table_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def teamplayers_get(self, season_name, team_id=3, league_id=1):
        """ get playerinformation per team via rest """
        # 1 - for DEL Regular season
        # 3 - for DEL Playoffs
        # 4 - for Magenta Cup
        self.logger.debug('DelAppHelper.teamplayers_get(%s:%s)\n', season_name, team_id)
        url = f'{self.del_api}/league-team-stats/{season_name}/{league_id}/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def teammatches_get(self, season_name, team_id=3, league_id=1):
        """ get matches for a certain team league_id - 1 regular, 3 playoff """
        self.logger.debug('DelAppHelper.teammatches_get(%s:%s:%s)\n', season_name, team_id, league_id)
        url = f'{season_name}/league-team-matches/{season_name}/{league_id}/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def teamstats_get(self, match_id, team_id):
        """ get teamstats_get from del.org """
        self.logger.debug('DelAppHelper.teamstats_get(%s:%s)\n', match_id, team_id)
        url = f'{self.del_api}/matches/{match_id}/team-stats/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def teamstatssummary_get(self, delseason, leagueid, team_id):
        """ get teamstats_get from del.org """
        self.logger.debug('DelAppHelper.teamstatssummary_get(%s:%s:%s)\n', delseason, leagueid, team_id)
        url = f'{self.del_api}/league-all-team-stats/{delseason}/{leagueid}/{team_id}.json'
        return requests.get(url, headers=self.headers, timeout=self.timeout, verify=False).json()

    def tournamentid_get(self):
        """ get tournament id """
        self.logger.debug('DelAppHelper.tournamentid_get() via mobile_api\n')
        data = {'requestName': 'tournamentList', 'lastUpdate': 0}
        result = self.api_post(self.mobile_api, data)
        if result:
            if 'tournamentID' in result[-1]:
                self.logger.debug('DelAppHelper.tournamentid_get() set tournament to: %s\n', result[-1]['tournamentID'])
                self.tournamentid = result[-1]['tournamentID']
        self.logger.debug('DelAppHelper.tournamentid_get() ended with: %s\n', self.tournamentid)
        return result
