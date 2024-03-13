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
        
    def step(self, tile, player_id, utility_matrix, dqn=False, action=None):
        """ Кладём тайл """

        # Получение списка из мест, куда можно положить тайл:
        tile_to_put = tile
        placetile = PlaceTile(self.board.board, tile_to_put)
        availible_places = placetile.availible_places()
        
        # Перекладываем в конец колоды, если некуда класть:
        if len(availible_places) == 0:
            return 
        
        # Сверяем, есть ли ненулевые элементы утилити матрицы:
        not_null_places = []
        is_null = 0
        for ind, place in enumerate(availible_places):
            coords = availible_places[ind][3]
            rotations = availible_places[ind][2]
            if utility_matrix[rotations, tile['ID'] - 1, coords[0], coords[1]] != 0:
                is_null += 1
                not_null_places.append(ind)
        
        
        if player_id== 0:
            
            if is_null == 0:            
                place = choice(availible_places)
            
            else:
                # decision making
                max_item = 0
                max_ind = not_null_places[0]
                for ind in not_null_places:
                    coords = availible_places[ind][3]
                    rotations = availible_places[ind][2]
                    value = utility_matrix[rotations, tile['ID'] - 1, coords[0], coords[1]]
                    if value > max_item:
                        max_item = value
                        max_ind = ind
                place = availible_places[max_ind]
            
        else:
            place = choice(availible_places) # RANDOM
            
        # Вращение и добавление ограничения в тайл:
        tile_to_put = placetile.change_tile(tile_to_put, *place)
        self.board.put_tile(tile_to_put)
        
        if dqn==True:
            temp_actions = self.board.add_action() + [1]
            temp_rewards = Rewards(temp_actions, self.board.board).reward_list

            return tile_to_put, temp_actions, temp_rewards
        
        # Действия: 1- для пропуска, остальное-это объекты на поле, куда можно положить тайл:
        actions = self.board.add_action() + [1]
        indices = list(range(len(actions)))
        rewards = Rewards(actions, self.board.board).reward_list
        action_ind = choice(indices)
        action_freedom = actions[action_ind]
        reward = rewards[action_ind]
        json_append_to('Visualize/meeples.json', [{'action':action_freedom, 'player': player_id, 'plotted': False}])
        
        # Закрытие объектов на поле, дороги с 2-мя концами, города закрытые со всех сторон, закрытые церкви
        self.board.close_action(action=action_freedom, player_ID=player_id) 
        try:
            a1, a2, a3, a4, a5 = reward, tile_to_put['rotated'], tile_to_put['ID'], tile_to_put['coord'][0], tile_to_put['coord'][1]
            return reward, tile_to_put['rotated'], tile_to_put['ID'], tile_to_put['coord'][0], tile_to_put['coord'][1]
        except:
            return [0, 0, 0, 0, 0]

    
    def end_game(self):
        # Сохранение картинки 
        # plot_board(self.board.board)  
                
        # Подсчёт очков
        PointsClosed().write()  
        PointsUnclosed(self.board.board)
        
        # Очки за завершённые объекты:
        points_0 = json_read('Data/Players.json')[0]['Points']
        points_1 = json_read('Data/Players.json')[1]['Points']    
        
        # if points_0 > points_1:
        #     print(f'winner- 0 with points = {points_0}')
        # elif points_0 < points_1:
        #     print(f'winner- 1 with points = {points_1}')
        # elif points_0 == points_1:
        #     print('No')
        return [points_0, points_1]
    
    @staticmethod
    def max_reward_action(actions):
        if len(actions) == 0:
            return {'index': -1}
        max_dict = max(actions, key=lambda x: x['reward'])
        return max_dict
    
    def select_action(self, action, actions, rewards):
        """Выбор того, что дала нейронка"""
        # Nothing:
        if action == 0 or len(actions) == 1:
            return len(actions) - 1
        
        items = []
        # Сортировка действий по их типам
        for ind, action_ in enumerate(actions[:-1]):
            items.append({'action': action_, 'index': ind, 'reward': rewards[ind]})
        
        if action == 1:
            action_type = [item for item in items if item['action']['type'] == 'road']
        elif action == 2:
            action_type = [item for item in items if item['action']['type'] == 'city']
        elif action == 3:
            action_type = [item for item in items if item['action']['type'] == 'church']

        decision_action = self.max_reward_action(action_type)
        return decision_action['index']

        
        
        
        
    
    
    def dqn_action(self, tile_to_put, actions, rewards, action, player_id=0):
    
        # Действия: 1- для пропуска, остальное-это объекты на поле, куда можно положить тайл:
        action_ind = self.select_action(action, actions, rewards)
        action_freedom = actions[action_ind]
        reward = rewards[action_ind]
        json_append_to('Visualize/meeples.json', [{'action':action_freedom, 'player': player_id, 'plotted': False}])

        # Закрытие объектов на поле, дороги с 2-мя концами, города закрытые со всех сторон, закрытые церкви
        self.board.close_action(action=action_freedom, player_ID=player_id) 
        return reward
        
    def dqn_state(self, tile_to_put, actions, rewards):
        
        state = np.linspace(0, 0, 17)
        player_stats = json_read('Data/Players.json')[0]
        
        # Количество очков и миплов
        state[0] = self.end_game()[0]
        state[1] = player_stats['Meeples']
        
        # Колиечство дорог, городов и церквей, на которых находится игрок
        for state_ind, object_type in zip([2, 3, 4], ['Roads', 'Cities', 'Churches']):
            objects = json_read(f'Data/Elements/{object_type}.json')
            for item in objects:
                if 0 in item['players']:
                    state[state_ind] += 1
        
        # Награды за дорогу, город и церковь, которые получит игрок присоединив тайл:
        reward_dict = {'road': 0, 'city': 0, 'church': 0}
        for action, reward in zip(actions[:-1], rewards[:-1]):
            reward_dict[action['type']] += reward
        for state_ind, reward_type in zip([5, 6, 7], ['road', 'city', 'church']):
            state[state_ind] += reward_dict[reward_type]
            
        # Закрытые концы у дороги:
        for road in [item for item in actions[:-1] if item['type'] == 'road']:
            state[8] += road['additional_points']
            if 1 in road['players']:
                state[11] += 1
            if 0 in road['players']:
                state[15] += 1
            
        # Щиты у города
        for city in [item for item in actions[:-1] if item['type'] == 'city']:
            state[9] += city['shield']
            state[10] += city['additional_points']
            if 1 in city['players']:
                state[11] += 1
            if 0 in city['players']:
                state[16] += 1
                
        for edge, value in tile_to_put['edges'].items():
            if 'R' in value:
                state[12] += 1
            elif 'C' in value:
                state[13] += 1
            elif 'G' in value:
                state[14] += 1
                
        return state
        
        
        
        

