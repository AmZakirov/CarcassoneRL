import numpy as np

class Mats:
    
    def __init__(self):
        
        self.alpha = 0.5
        self.gamma = 0.5
        self.utility_matrix = np.zeros((4, 24, 71, 71))
        
        
    def update_utility(self, rotation, tile_num, reward, x, y, previous):
        
        value = self.alpha * (reward + self.gamma * self.utility_matrix[rotation, tile_num-1, x, y])
        self.utility_matrix[previous]  = self.utility_matrix[previous] * (1 - self.alpha) + value
        
