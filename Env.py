from Bin.Board import Board
from Bin.Place import PlaceTile
from Bin.Player import PointsClosed, PointsUnclosed, Rewards

from Visualize.Visualizer import plot_board
from FileActions import json_read, json_write, json_append_to               # pip install InnoFileManager
from random import choice, shuffle
import copy
import numpy as np
import matplotlib.pyplot as plt
from random import randint

class Carcassone:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        " Обнуляем файлы "
        tiles = json_read('Data/Tiles_initial.json')
        json_write('Data/Elements/Roads.json', [])
        json_write('Data/Elements/Churches.json', [])
        json_write('Data/Elements/Cities.json', [])
        json_write('Data/Elements/Fields.json', [])
        json_write('Visualize/meeples.json', [])
        json_write('Data/Players.json', [{'ID': ID, 'Meeples': 8, 'Points': 0, 'Roads': [], 'Churches': [], 'Cities': []} for ID in range(2)])

        " Инициализируем доску "
        # Инициализация доски: Кладём первый тайл
        board = Board()
            
        # Определяем порядок выкладывания тайлов
        all_tiles = []
        for tile in tiles:
            tiles_by_ID = [copy.deepcopy(tile) for ind in range(tile['counts'])]
            all_tiles += tiles_by_ID
        shuffle(all_tiles)
        
        self.board = board
        self.tiles = all_tiles
        
    def step(self, tile, player_id):
        """ Кладём тайл """

        # Получение списка из мест, куда можно положить тайл:
        tile_to_put = tile
        placetile = PlaceTile(self.board.board, tile_to_put)
        availible_places = placetile.availible_places()
        
        # Перекладываем в конец колоды, если некуда класть:
        if len(availible_places) == 0:
            return 
        
        if player_id== 0:
            place = choice(availible_places) # TODO: DECISION MAKING
        else:
            place = choice(availible_places) # RANDOM
            
        # Вращение и добавление ограничения в тайл:
        tile_to_put = placetile.change_tile(tile_to_put, *place)
        self.board.put_tile(tile_to_put)
        
        # Действия: 1- для пропуска, остальное-это объекты на поле, куда можно положить тайл:
        actions = self.board.add_action() + [1]
        rewards = Rewards(actions, self.board.board).reward_list
        
        if player_id == 0:
            action_freedom = choice(actions)  #TODO: DECISION MAKING
        else:
            action_freedom = choice(actions)  #RANDOM
        json_append_to('Visualize/meeples.json', [{'action':action_freedom, 'player': player_id, 'plotted': False}])
        
        # Закрытие объектов на поле, дороги с 2-мя концами, города закрытые со всех сторон, закрытые церкви
        self.board.close_action(action=action_freedom, player_ID=player_id) 
        return
    
    def end_game(self):
        # Сохранение картинки 
        plot_board(self.board.board)  
                
        # Подсчёт очков
        PointsClosed().write()  
        PointsUnclosed(self.board.board)
        
        # Очки за завершённые объекты:
        points_0 = json_read('Data/Players.json')[0]['Points']
        points_1 = json_read('Data/Players.json')[1]['Points']    
        
        if points_0 > points_1:
            print(f'winner- 0 with points = {points_0}')
        elif points_0 < points_1:
            print(f'winner- 1 with points = {points_1}')
        elif points_0 == points_1:
            print('No')

