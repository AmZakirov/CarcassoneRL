import numpy as np
from FileActions import *

_dict_path = 'Data/Players.json'

        
class Player:

    def __init__(self, ID):
        self.ID = ID
        self.players_list = json_read(_dict_path)
    
    def put_meeple(self):
        if self.players_list[self.ID]['Meeples'] > 0:
            self.players_list[self.ID]['Meeples'] -= 1
    
    def return_meeple(self, counts):
        self.players_list[self.ID]['Meeples'] += counts
    
    def add_item(self, key, item):
        self.players_list[self.ID][key].append(item)

    def write(self, player_list):
        self.players_list[0] = player_list[0]
        self.players_list[1] = player_list[1]
        json_write(_dict_path, self.players_list)
    
    def add_points(self, points):
        self.players_list[self.ID]['Points'] += points


class PointsClosed:
    
    def __init__(self):
        pass
        
    def count_closed(self):
        
        players_points = []
        for ID in range(2):
            
            player_points = 0
            player_dict = json_read(_dict_path)[ID]
            
            for city in player_dict['Cities']:
                player_points += self._count_cities(city)
            
            for road in player_dict['Roads']:
                player_points += self._count_roads(road)
                
            for church in player_dict['Churches']:
                player_points += 9
                
            players_points.append(player_points)
        return players_points

    def write(self):
        self.points = self.count_closed()
        
        players_dict = json_read(_dict_path)
        for ID in range(2):
            players_dict[ID]['Points'] = self.points[ID]
        json_write(_dict_path, players_dict)
        return
                
    def _count_cities(self, city):
        
        points = 0
        city_tiles = len(city['indices'])
        add_points = city['additional_points']
        shields = city['shield']
        points = city_tiles + add_points + shields * 2
        
        if city['is_open'] == False:
            points *= 2
        return points
    
    def _count_roads(self, road):
        
        points = 0
        road_tiles = len(road['indices'])
        add_points = road['additional_points']
        points = road_tiles + add_points
        return points
    
    def __count_churches(self, church):
        
        return 9
    
    
class PointsUnclosed(PointsClosed):
    
    def __init__(self, board):
        self.board = board
        self.x = np.shape(board)[0]
        self.y = np.shape(board)[1]
        self.roads = json_read('Data/Elements/Roads.json')
        self.cities = json_read('Data/Elements/Cities.json')
        self.churches = json_read('Data/Elements/Churches.json')
        self.fields = json_read('Data/Elements/Fields.json')
        
        self.player0 = Player(0)
        self.player1 = Player(1)
        
        self.count_roads_and_cities()
        self.count_churches()
        
        self.player0.write([self.player0.players_list[0], self.player1.players_list[1]])
    
    def count_roads_and_cities(self):
        
        count_funcs = [self._count_roads, self._count_cities]
        for ind, item in enumerate([self.roads, self.cities]):
            for object_ in item:
                players = object_['players']
                points = count_funcs[ind](object_)
                
                if len(players) != 0:
                    count_0, count_1 = players.count(0), players.count(1)
                    
                    if count_0 == count_1:
                        self.player0.add_points(points)
                        self.player1.add_points(points)
                    
                    if count_0 > count_1:
                        self.player0.add_points(points)
                    
                    if count_0 < count_1:
                        self.player1.add_points(points)
    
    def count_churches(self):
        
        for ind, church in enumerate(self.churches):
            
            if len(church['players']) == 1:
                player = church['players'][0]
                inds = church['indices']
                counter = 0
                for i in range(inds[0] - 1, inds[0] + 2):
                    for j in range(inds[1] - 1, inds[1] + 2):
                        if type(self.board[i, j]) == dict:
                            counter += 1
                if player == 0:
                    self.player0.add_points(counter)
                else:
                    self.player1.add_points(counter)
            
                
class Rewards:
    
    def __init__(self, actions, board):
        self.actions = actions
        self.board = board
        
    @property
    def reward_list(self):
        rewards = [0] * len(self.actions)
        
        for ind in range(len(self.actions)):
            if type(self.actions[ind]) == int:
                continue
            if self.actions[ind]['type'] == 'road':
                rewards[ind] = self._count_roads(self.actions[ind])
            elif self.actions[ind]['type'] == 'city':
                rewards[ind] = self._count_cities(self.actions[ind])
            elif self.actions[ind]['type'] == 'church':
                rewards[ind] = self._count_churches(self.actions[ind])
        return rewards
    
    def _count_roads(self, road):
        return len(road['indices']) + road['additional_points']
    
    def _count_cities(self, city):
        return len(city['indices']) + city['additional_points'] + city['shield'] * 2
    
    def _count_churches(self, church):
        
        ind_pair = church['indices']            
        counter = 0
        for i in range(ind_pair[0] - 1, ind_pair[0] + 2):
            for j in range(ind_pair[1] - 1, ind_pair[1] + 2):
                if type(self.board[i, j]) == dict:
                    counter += 1
        return counter
    