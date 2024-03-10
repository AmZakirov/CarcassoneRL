import numpy as np
from FileActions import *
from Bin.Player import Player

class City_options:
    
    def __init__(self, board):
        self.board = board
        self.cities = json_read('Data/Elements/Cities.json')
        self.last_city_ID = max([item['ID'] for item in self.cities]) if len(self.cities) > 0 else 0

    def _add_city(self, is_open, inds, with_shield):
        self.last_city_ID += 1
        shields = 0
        if with_shield == True:
            shields += 1
        return {'ID': self.last_city_ID, 'indices': inds, 'is_open': is_open, 'players': [], 'type': 'city', 'shield': shields, 'additional_points': 0}
    
    def _find_city_edges(self, i, j):
        
        directions = []
        for k, v in self.board[i, j]['edges'].items():
            
            if "C" in v:
                directions.append(k)
        return directions
    
    @staticmethod
    def _indices_by_direction(direction, i, j):
        
        directions = ["left", "right", "up", "down"]
        indices = [[i, j-1], [i, j+1], [i-1, j], [i+1, j]]
        return indices[directions.index(direction)]
        
    def _count_unconstrained(self, tile: dict)-> int:
        
        counter = 0
        for k, v in tile['edges'].items():
            if 'C' in v:
                counter += 1
        return counter

    def _count_constrained(self, tile: dict)-> int:
        
        counter = 0
        for k, v in tile['edges'].items():
            if 'constrained C' == v:
                counter += 1
        
        if counter == 0:
            return 0
        
        return counter
    
    def _find_constrained_direction(self, i, j):
        
        keys = []
        for k, v in self.board[i, j]['edges'].items():
            if 'constrained C' == v:
                keys.append(k)
        
        indices = []
        for k in keys:
            if k == "left":
                indices.append([i, j-1])
            elif k == "right":
                indices.append([i, j+1])
            elif k == "up":
                indices.append([i-1, j])
            elif k == "down":
                indices.append([i+1, j])
        
        return indices


class Cities(City_options):
    
    def __init__(self, board, tile):
        City_options.__init__(self, board)
        self.tile = tile
        self.constrained_counter = self._count_constrained(tile)
        self.unconstrained_counter = self._count_unconstrained(tile)
        self.city_manager()
        
        
    def city_manager(self):
        ''' Смотрим на тайл и определяем его судьбу '''      
        
        if self.tile.get('separate') != True and self.unconstrained_counter > 0:
            self.no_separatists()
        
        if self.tile.get('separate') == True:
            self.add_separatist()        
        
        json_write('Data/Elements/Cities.json', self.cities)        
                        
    def no_separatists(self):
        ''' Операции с тайлами без разделения '''
        shield_bool = True if self.tile.get('shield') else False
        # Создание города, если не закреплён:
        if self.constrained_counter == 0:
            self.cities.append(self._add_city(is_open=True, inds=[self.tile['coord']], with_shield=shield_bool))

        # Объединения с закрепленными городами:
        if self.constrained_counter > 0:
            ind_pairs = self._find_constrained_direction(*self.tile['coord'])
            new_city = self._add_city(is_open=True, inds = [self.tile['coord']], with_shield=shield_bool)
            city_counter = 0
            for ind_pair in ind_pairs:
                for city in self.cities:
                    for indices in city['indices']:
                        if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                            new_city['indices'] += city['indices']
                            new_city['players'] += city['players']
                            new_city['additional_points'] += city['additional_points']
                            if city['shield'] != 0:
                                new_city['shield'] += city['shield']
                            self.cities.remove(city)
                            city_counter += 1       # Для учёта разделительных тайлов
            
            
            if city_counter < self.constrained_counter:
                new_city['additional_points'] = self.constrained_counter - city_counter
            
            self.cities.append(new_city)
            
            
    
    def add_separatist(self):
        ''' Операции с разделительными тайлами '''
        if self.constrained_counter >= 1:
            ind_pairs = self._find_constrained_direction(*self.tile['coord'])
            for ind_pair in ind_pairs:
                for ind, city in enumerate(self.cities):
                    for indices in city['indices']:
                        if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                            self.cities[ind]['additional_points'] += 1
                            
                
            
    def close_cities(self):
        
        City_options.__init__(self, self.board)
        for ind, city in enumerate(self.cities):
            constrained_counter, unconstrained_counter = 0, 0
            
            for ind_pair in city['indices']:
                tile = self.board[ind_pair[0], ind_pair[1]]
                constrained_counter += self._count_constrained(tile)
                unconstrained_counter += self._count_unconstrained(tile)
            
            if constrained_counter == unconstrained_counter and self.cities[ind]['is_open'] == True:
                self.cities[ind]['is_open'] = False
                players_in_city = self.cities[ind]['players']
                
                if len(players_in_city) != 0:
                    
                    count_0, count_1 = players_in_city.count(0), players_in_city.count(1)
                    player0 = Player(0)
                    player1 = Player(1)
                    
                    if count_0 == count_1:
                        player0.add_item("Cities", city)
                        player1.add_item("Cities", city)
                    
                    elif count_0 > count_1:
                        player0.add_item("Cities", city)
                    
                    elif count_0 < count_1:
                        player1.add_item("Cities", city)
                    
                    if count_0 != 0:
                        player0.return_meeple(count_0)
                    
                    if count_1 != 0:
                        player1.return_meeple(count_1)
                    
                    player0.write([player0.players_list[0], player1.players_list[1]])
                        
                
        json_write('Data/Elements/Cities.json', self.cities)
        
    @property
    def free_cities(self):
        places_to_put = []
        for ind, city in enumerate(self.cities):
            if self.tile['coord'] in city['indices']:
                if city['is_open'] == True and len(city['players']) == 0:
                    places_to_put.append(city)
        return places_to_put
        
        
                


        
