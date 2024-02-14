import numpy as np
import copy
from FileActions import *

from Bin.Elements.Roads import *
from Bin.Elements.Churches import Churches
from Bin.Elements.Cities import Cities
from Bin.Player import Player

class Tile_actions:
    
    def __init__(self, board):
        self.board = board
    
    @staticmethod
    def tile_properties(tile: dict, GameID: int, coord: list)-> dict:
        '''
        Копируем во избежание конфликтов тайл и дополняем его свойства:
        уникальным GameID (порядок размещения на доске),
        координатами coord (индексы строки и столбца в numpy массиве)
        '''
        tile_dict = copy.copy(tile)
        tile_dict['GameID'] = GameID
        tile_dict['coord'] = coord
        return tile_dict
    
    
    def search_latest_GameID(self):
        ''' 
        Пробегаем всю доску и ищем максимальный GameID 
        '''
        max_GameID = 0
        for i in range(self.x):
            for j in range(self.y):
                if type(self.board[i, j]) == dict:
                    if self.board[i, j]['GameID'] > max_GameID:
                        max_GameID = self.board[i, j]['GameID']
        return max_GameID
    
    
    def search_tile_by_GameID(self, GameID: int):
        '''
        Пробегаем доску и ищем тайл по GameID
        '''
        for i in range(self.x):
            for j in range(self.y):
                if type(self.board[i, j]) == dict:
                    if self.board[i, j]['GameID'] == GameID:
                        return self.board[i, j]
    
    def search_tile_by_ID(self, ID: int):
        '''
        Пробегаем начальные тайлы и ищем ID
        '''
        for tile in self.initial_tiles:
            if tile['ID'] == ID:
                return tile['edges']

class Board(\
    Tile_actions
    ):
    
    def __init__(self):
        ''' При инициализации выкладываем на доску старотовый тайл '''
        self.board = np.zeros((100, 100), dtype=object)
        self.x = np.shape(self.board)[0]
        self.y = np.shape(self.board)[1]
        
        start_tile = json_read('Data/Tiles_initial.json')[19]
        self.board[50, 50] = self.tile_properties(start_tile, GameID=0, coord=[50, 50]) 
        Roads(self.board, self.board[50, 50]).close_roads()
        Cities(self.board, self.board[50, 50]).close_cities()
        
        self.__update_board(to_write=True)
        
        
    def put_tile(self, tile):
        ''' Добавляем тайл на доску '''
        i, j = tile['coord'][0], tile['coord'][1]
        self.tile_i, self.tile_j = i, j
        self.board[i, j] = tile
        self.board[i, j]['GameID'] = self.last_GameID + 1
        self.__add_constrainded(i, j)
        self.__update_board(to_write=True)
        
    def add_action(self):
        ''' Получение списка возможных положений для мипла игрока '''
        tile = self.board[self.tile_i, self.tile_j] 
        self.road_actions = Roads(self.board, tile)
        self.church_actions = Churches(self.board, tile)
        self.cities_actions = Cities(self.board, tile)
        
        action_freedom = []
        action_freedom += self.road_actions.free_roads
        action_freedom += self.church_actions.free_churches
        action_freedom += self.cities_actions.free_cities
        return action_freedom
    
    def close_action(self, action=None, player_ID=None):
        ''' Закрываем объекты на карте и возвращем фишки '''
        if action == 1:
            pass
        else:
            if action['type'] == 'road':
                filename = 'Data/Elements/Roads.json'
            if action['type'] == 'city':
                filename = 'Data/Elements/Cities.json'
            if action['type'] == 'church':
                filename = 'Data/Elements/Churches.json'

            items = json_read(filename)
            for ind in range(len(items)):
                if items[ind]['ID'] == action['ID']:
                    player = Player(player_ID)
                    player.put_meeple()
                    player.write(player.players_list)
                    items[ind]['players'].append(player_ID)
                    json_write(filename, items)
                    break
            
        self.road_actions.close_roads()
        self.church_actions.close_churches()
        self.cities_actions.close_cities()

    
    def __update_board(self, to_write=False):
        
        self.last_GameID = self.search_latest_GameID()
        if to_write: 
            tiles_in_board = []
            for i in range(self.x):
                for j in range(self.y):
                    if type(self.board[i, j]) == dict:
                        tiles_in_board.append(self.board[i, j])
            
            json_write('Data/Tiles_in_board.json', tiles_in_board)
        
        
    def __add_constrainded(self, i, j):
        
        indices = [[i-1, j], [i+1, j], [i, j-1], [i, j+1]]
        directions = ['down', 'up', 'right', 'left']
        opposites = {"left": "right", "right": "left", "up": "down", "down": "up"}
        
        for pair, direction in zip(indices, directions):
            if type(self.board[pair[0], pair[1]]) == dict:
                self.board[pair[0], pair[1]]['edges'][direction] = f"constrained {self.board[pair[0], pair[1]]['edges'][direction]}"
                self.board[i, j]['edges'][opposites[direction]] = f"constrained {self.board[i, j]['edges'][opposites[direction]]}"
        
            
            
            
        
        
        
        
            
        
