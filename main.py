from Bin.Board import Board
from Bin.Place import PlaceTile
from Bin.Player import PointsClosed

from Visualize.Visualizer import plot_board
from FileActions import json_read, json_write               # pip install InnoFileManager
from random import choice, shuffle
import copy
import numpy as np
import matplotlib.pyplot as plt
from random import randint

tiles = json_read('Data/Tiles_initial.json')
json_write('Data/Elements/Roads.json', [])
json_write('Data/Elements/Churches.json', [])
json_write('Data/Elements/Cities.json', [])
json_write('Data/Players.json', [{'ID': ID, 'Meeples': 8, 'Points': 0, 'Roads': [], 'Churches': [], 'Cities': []} for ID in range(2)])

def main():
    
    # Инициализация доски: Кладём первый тайл
    board = Board()
    
    # Определяем порядок выкладывания тайлов
    all_tiles = []
    for tile in tiles:
        tiles_by_ID = [copy.deepcopy(tile) for ind in range(tile['counts'])]
        all_tiles += tiles_by_ID
    shuffle(all_tiles)
    
    # Цикл по выложенным тайлам:
    for ind, tile_to_put in enumerate(all_tiles):
        
        player_id = ind % 2
        # Получение списка из мест, куда можно положить тайл
        placetile = PlaceTile(board.board, tile_to_put)
        availible_places = placetile.availible_places()
        
        if len(availible_places) == 0:
            pass #TODO: Переложить тайл в конец колоды
        
        else:
            if player_id== 0:
                place = choice(availible_places) # TODO: DECISION MAKING
            else:
                place = choice(availible_places) # RANDOM
                
            # Вращение и добавление ограничения в тайл
            tile_to_put = placetile.change_tile(tile_to_put, *place)
            board.put_tile(tile_to_put)
            
            # Действия: 1- для пропуска, остальное-это объекты на поле, куда можно положить тайл
            actions = board.add_action() + [1]
            
            if player_id == 0:
                action_freedom = choice(actions)  #TODO: DECISION MAKING
            else:
                action_freedom = choice(actions)  #RANDOM
            
            # Закрытие объектов на поле, дороги с 2-мя концами, города закрытые со всех сторон, закрытые церкви
            board.close_action(action_freedom, player_ID=player_id)   
    
    # Подсчёт очков
    PointsClosed()           
    # Сохранение картинки 
    plot_board(board.board)      
        
    # Очки за завершённые объекты:
    points_0 = json_read('Data/Players.json')[0]['Points']
    points_1 = json_read('Data/Players.json')[1]['Points']    

main()