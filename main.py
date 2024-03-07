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
from itertools import chain


tiles = json_read('Data/Tiles_initial.json')
json_write('Data/Elements/Roads.json', [])
json_write('Data/Elements/Churches.json', [])
json_write('Data/Elements/Cities.json', [])
json_write('Data/Elements/Fields.json', [])
json_write('Visualize/meeples.json', [])
json_write('Data/Players.json', [{'ID': ID, 'Meeples': 8, 'Points': 0, 'Roads': [], 'Churches': [], 'Cities': []} for ID in range(2)])

def action_prepare(board, availible_places, placetile, tile_to_put):
    """Получаем 1д список всех возможных действий"""
    
    # Копируем классы доски перед тем, как мы положим на неё каждый тайл:
    list_creator = lambda item : [copy.deepcopy(item) for i in range(len(availible_places))]
    chain_convert = lambda ex_list: list(chain.from_iterable(ex_list))
    
    boards = list_creator(copy.deepcopy(board))
    tiles_to_put = list_creator(copy.deepcopy(tile_to_put))
    actions = list_creator(0)
    rewards = list_creator(0)
    len_array = list_creator(0)
    
    # Пробегаем по каждому возможному положению тайла, и получаем списки действий для каждого из них
    for ind, place in enumerate(availible_places):
        
        # Вращение и добавление ограничения в тайл:
        tiles_to_put[ind] = placetile.change_tile(tiles_to_put[ind], *place)
        boards[ind].put_tile(tiles_to_put[ind])
        
        # Действия: 1- для пропуска, остальное-это объекты на поле, куда можно положить тайл:
        actions_chunk = boards[ind].add_action() + [1]
        actions[ind] = actions_chunk
        rewards[ind] = Rewards(actions[ind], boards[ind].board).reward_list
        
        # Список длин для определения индекса доски потом
        if ind != 0:
            len_array[ind] = len_array[ind-1] + len(actions[ind])
        else:
            len_array[ind] = len(actions[ind])
            
    # Преобразуем всё в 1д и возвращаем
    actions_1d, rewards_1d = [chain_convert(item) for item in [actions, rewards]]
    return boards, tiles_to_put, actions_1d, rewards_1d, len_array

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
    unputted_tiles = []
    flag = False
    for j in range(2):
        if len(unputted_tiles) == 0 and not flag:
            tiles0 = all_tiles
        elif len(unputted_tiles) == 0 and flag:
            break
        else:
            tiles0 = unputted_tiles
        
        for ind, tile_to_put in enumerate(tiles0[:20]):
            
            player_id = ind % 2
            # Получение списка из мест, куда можно положить тайл:
            placetile = PlaceTile(board.board, tile_to_put)
            availible_places = placetile.availible_places()
            
            # Перекладываем в конец колоды:
            if len(availible_places) == 0:
                unputted_tiles.append(tile_to_put)
            
            else:
                """
                Короче, 
                actions_1d - это наш список, из которого мы должны что-то выбирать
                Мы выбираем из него действие, и сохраняем переменную в action_freedom
                Награда за него - reward
                """
                " Мы копируем экземпляры досок, чтобы потом оставить только выбранный "
                boards, tiles_to_put, actions_1d, rewards_1d, len_array  = action_prepare(board, availible_places, placetile, tile_to_put)
                
                if player_id == 0:
                    action_freedom = choice(actions_1d)  #TODO: DECISION MAKING
                else:
                    action_freedom = choice(actions_1d)  #RANDOM
                    
                action_index = actions_1d.index(action_freedom)
                reward = rewards_1d[action_index]
                
                # Ищем доску, к которой мы относим наше действие:
                for item in len_array:
                    if action_index < item:
                        board = boards[len_array.index(item)]
                        break

                json_append_to('Visualize/meeples.json', [{'action':action_freedom, 'player': player_id, 'plotted': False}])
                # Закрытие объектов на поле, дороги с 2-мя концами, города закрытые со всех сторон, закрытые церкви
                board.close_action(action=action_freedom, player_ID=player_id) 
            
            flag = True
    # Сохранение картинки 
    plot_board(board.board)  
            
    # Подсчёт очков
    PointsClosed().write()  
    PointsUnclosed(board.board)
    
    # Очки за завершённые объекты:
    points_0 = json_read('Data/Players.json')[0]['Points']
    points_1 = json_read('Data/Players.json')[1]['Points']    

main()
