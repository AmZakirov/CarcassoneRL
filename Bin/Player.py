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

    def write(self):
        json_write(_dict_path, self.players_list)

class PointsClosed:
    
    def __init__(self):
        self.points = self.count_closed()
        self.write()
        
    def count_closed(self):
        
        players_points = []
        for ID in range(2):
            
            player_points = 0
            player_dict = json_read(_dict_path)[ID]
            
            for city in player_dict['Cities']:
                player_points += self.__count_cities(city)
            
            for road in player_dict['Roads']:
                player_points += self.__count_roads(road)
                
            for church in player_dict['Churches']:
                player_points += 9
                
            players_points.append(player_points)
        return players_points

    def write(self):
        players_dict = json_read(_dict_path)
        for ID in range(2):
            players_dict[ID]['Points'] = self.points[ID]
        json_write(_dict_path, players_dict)
        return
            
    
    def __count_cities(self, city):
        
        points = 0
        city_tiles = len(city['indices'])
        add_points = city['additional_points']
        shields = city['shield']
        points = city_tiles + add_points + shields * 2
        
        if city['is_open'] == False:
            points *= 2
        return points
    
    def __count_roads(self, road):
        
        points = 0
        road_tiles = len(road['indices'])
        add_points = road['additional_points']
        points = road_tiles + add_points
        return points
    
    def __count_churches(self, church):
        
        return 9