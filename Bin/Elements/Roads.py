import numpy as np
from FileActions import *
from Bin.Player import Player

class Road_options:
    
    def __init__(self, board):
        self.board = board
        self.roads = json_read('Data/Elements/Roads.json')
        self.last_road_ID = max([item['ID'] for item in self.roads]) if len(self.roads) > 0 else 0

    def _add_road(self, is_open, inds):
        self.last_road_ID += 1
        return {'ID': self.last_road_ID, 'indices': inds, 'is_open': is_open, 'additional_points': 0, 'players': [], 'type': 'road'}
    
    def _find_road_edges(self, i, j):
        
        directions = []
        for k, v in self.board[i, j]['edges'].items():
            
            if "R" in v:
                directions.append(k)
        return directions
    
    @staticmethod
    def _indices_by_direction(direction, i, j):
        
        directions = ["left", "right", "up", "down"]
        indices = [[i, j-1], [i, j+1], [i-1, j], [i+1, j]]
        return indices[directions.index(direction)]
        
    def _count_unconstrained(self, tile)-> int:
        
        counter = 0
        for k, v in tile['edges'].items():
            if 'R' in v:
                counter += 1
        return counter

    def _count_constrained(self, tile):
        
        counter = 0
        for k, v in tile['edges'].items():
            if 'constrained R' == v:
                counter += 1
        
        if counter == 0:
            return 0
        
        return counter
    
    def _find_constrained_direction(self, i, j):
        
        keys = []
        for k, v in self.board[i, j]['edges'].items():
            if 'constrained R' == v:
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


class Roads(Road_options):
    
    def __init__(self, board, tile):
        Road_options.__init__(self, board)
        self.tile = tile
        self.constrained_counter = self._count_constrained(tile)
        self.unconstrained_counter = self._count_unconstrained(tile)
        self.road_manager()
        
        
    def road_manager(self):
        ''' Смотрим на тайл и определяем его судьбу '''
        if self.unconstrained_counter == 0:
            pass
        
        elif self.unconstrained_counter == 1:
            self.single_edge()
        
        elif self.unconstrained_counter == 2:
            self.double_edges()
        
        elif self.unconstrained_counter > 2:
            self.crossroads()
        
        json_write('Data/Elements/Roads.json', self.roads)
                
            
    def single_edge(self):
        ''' Добавляем поинт к закрытой дороге '''
        if self.constrained_counter == 1:
            ind_pairs = self._find_constrained_direction(*self.tile['coord'])
            for ind_pair in ind_pairs:
                for ind, road in enumerate(self.roads):
                    for indices in road['indices']:
                        if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                            self.roads[ind]['additional_points'] += 1
                            return
    
    def double_edges(self):        
        ''' Все операции для тайлов с двумя дорогами '''
        # Без объединения:
        if self.constrained_counter == 0:
            self.roads.append(self._add_road(inds=[self.tile['coord']] , is_open=True))
            return
        # Примыкает к дороге, или объединяет 2:
        elif self.constrained_counter in [1, 2]:
            ind_pairs = self._find_constrained_direction(*self.tile['coord'])
            new_road = self._add_road(is_open=True, inds = [self.tile['coord']])
            road_counter = 0
            for ind_pair in ind_pairs:
                for road in self.roads:
                    for indices in road['indices']:
                        if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                            new_road['indices'] += road['indices']
                            new_road['players'] += road['players']
                            if road['additional_points'] == 1:
                                new_road['additional_points'] += 1
                            self.roads.remove(road)
                            road_counter += 1
            self.roads.append(new_road)
            
            " Учёт однодорожных тайлов "
            if road_counter == 0:
                new_road['additional_points'] += self.constrained_counter
    
    def crossroads(self):
        ''' Перекрёстки '''
        ind_pairs = self._find_constrained_direction(*self.tile['coord'])
        for ind_pair in ind_pairs:
            for ind, road in enumerate(self.roads):
                for indices in road['indices']:
                    if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                        self.roads[ind]['additional_points'] += 1
            
    def close_roads(self):
        Road_options.__init__(self, self.board)
        for ind, road in enumerate(self.roads):
            if road['additional_points'] == 2 and self.roads[ind]['is_open'] == True:
                self.roads[ind]['is_open'] = False
                players_in_road = self.roads[ind]['players']
                
                if len(players_in_road) != 0:
                    
                    count_0, count_1 = players_in_road.count(0), players_in_road.count(1)
                    player0 = Player(0)
                    player1 = Player(1)
                    
                    if count_0 == count_1:
                        player0.add_item("Roads", road)
                        player1.add_item("Roads", road)
                    
                    elif count_0 > count_1:
                        player0.add_item("Roads", road)
                    
                    elif count_0 < count_1:
                        player1.add_item("Roads", road)
                    
                    if count_0 != 0:
                        player0.return_meeple(count_0)
                    
                    if count_1 != 0:
                        player1.return_meeple(count_1)
                    
                    player0.write([player0.players_list[0], player1.players_list[1]])
                        
                        
        json_write('Data/Elements/Roads.json', self.roads)
        
    @property
    def free_roads(self):
        places_to_put = []
        for ind, road in enumerate(self.roads):
            if self.tile['coord'] in road['indices']:
                if road['is_open'] == True and len(road['players']) == 0:
                    places_to_put.append(road)
        
        if self.unconstrained_counter in [1, 3, 4]:
            ind_pairs = self._find_constrained_direction(*self.tile['coord'])
            for ind_pair in ind_pairs:
                for road in self.roads:
                    for indices in road['indices']:
                        if ind_pair[0] == indices[0] and ind_pair[1] == indices[1]:
                            if road['is_open'] == True and len(road['players']) == 0:
                                places_to_put.append(road)
        return places_to_put
                


        
