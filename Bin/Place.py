import numpy as np
import copy

class PlaceTile:
    
    def __init__(self, board: np.zeros, tile: dict):
        self.tile = tile
        self.board = board
        self.x = np.shape(board)[0]
        self.y = np.shape(board)[1]
        
    
    def availible_places(self):
        
        availible_places = []
        for i in range(self.x):
            for j in range(self.y):
                
                if type(self.board[i, j]) == dict:
                    tile = self.board[i, j]

                    for k, v in tile['edges'].items():

                        if "constrained" not in v:
                            
                            possible_orientations = self.check_neighbors(tile, k, i, j)
                            # print(v, possible_orientations)
                            if len(possible_orientations) != 0:
                                
                                availible_places += possible_orientations
        
        return availible_places
                        

    
    def check_neighbors(self, tile: dict, direction: str, i, j):
        ''' 
        Проверяем соседей и их края
        direction - сторона к которой мы присоединяем тайл
        neighbours - соседи
        neighbour edges - стороны соседей
        '''
        
        if direction == "left":
            neighbours = [self.board[i-1, j-1], self.board[i+1, j-1], self.board[i, j-2], self.board[i, j]]
            neighbour_edges = ["down", "up", "right", direction]
            place_ind = [i, j-1]
            opposite_direction = "right"
        
        elif direction == "right":
            neighbours = [self.board[i-1, j+1], self.board[i+1, j+1], self.board[i, j+2], self.board[i, j]]
            neighbour_edges = ["down", "up", "left", direction]
            place_ind = [i, j+1]
            opposite_direction = "left"

        elif direction == "up":
            neighbours = [self.board[i-1, j-1], self.board[i-1, j+1], self.board[i-2, j], self.board[i, j]]
            neighbour_edges = ["right", "left", "down", direction]
            place_ind = [i-1, j]
            opposite_direction = "down"

        elif direction == "down":
            neighbours = [self.board[i+1, j-1], self.board[i+1, j+1], self.board[i+2, j], self.board[i, j]]
            neighbour_edges = ["right", "left", "up", direction]
            place_ind = [i+1, j]
            opposite_direction = "up"

        
        possible_orientations = []
        for rotate_num in range(4):
            
            edges = self.__rotate_tile(self.tile, rotate_num)
            
            if self.__check_fit(edges, neighbours, neighbour_edges) == True:
                possible_orientations.append([edges, rotate_num, place_ind, direction, opposite_direction])
                
        return possible_orientations
            
            
    @staticmethod
    def __rotate_tile(tile, rotate_num):
        
        edges = copy.deepcopy(tile['edges'])
        
        if rotate_num == 0:
            return edges
                
        if rotate_num == 1:
            edge_dict = {'left': edges['down'], 'up': edges['left'], 'right': edges['up'], 'down': edges['right']}

        if rotate_num == 2:
            edge_dict = {'left': edges['right'], 'up': edges['down'], 'right': edges['left'], 'down': edges['up']}

        if rotate_num == 3:
            edge_dict = {'left': edges['up'], 'up': edges['right'], 'right': edges['down'], 'down': edges['left']}
        
        return edge_dict
        
    
    def __check_fit(self, edges, neighbours, neighbour_edges):
        
        counter = 0
        dict_to_compare = {"left":"right", "up":"down", "right": "left", "down": "up"}
                
        for ind, neighbour in enumerate(neighbours):

            if type(neighbour) == dict:
                
                if neighbour['edges'][neighbour_edges[ind]] == edges[dict_to_compare[neighbour_edges[ind]]]:
                    counter += 1
            
            else:
                counter += 1

        if counter == 4:
            return True
        
        return False
    
    @staticmethod
    def change_tile(tile, new_edges, rotations, coords, direction, opposite_direction):
        tile = copy.deepcopy(tile)
        tile['edges'] = new_edges
        tile['rotated'] = rotations
        tile['coord'] = coords
        tile['direction'] = direction
        tile['opposite_direction'] = opposite_direction
        return tile
        
