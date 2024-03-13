import numpy as np
from copy import deepcopy
from FileActions import *

class Fields:
    
    def __init__(self, board, tile):
        self.board = board
        self.tile = tile
        
        self.cities = json_read('Data/Elements/Cities.json')
        self.roads = json_read('Data/Elements/Roads.json')
        self.churches = json_read('Data/Elements/Churches.json')
        self.fields = json_read('Data/Elements/Fields.json')
    
    
    
    
    