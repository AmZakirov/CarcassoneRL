import numpy as np
from FileActions import *
from Bin.Player import Player


class Churches:
    
    def __init__(self, board, tile):
        self.board = board
        self.tile = tile
        self.churches = json_read('Data/Elements/Churches.json')
        self.last_church_ID = max([item['ID'] for item in self.churches]) if len(self.churches) > 0 else 0
        self._place_church()
    
    def _add_church(self, inds):
        self.last_church_ID += 1
        return {'ID': self.last_church_ID, 'indices': inds, 'players': [], 'is_open': True, 'type': 'church'}
    
    def _place_church(self):
        if self.tile.get('church') == True:
            self.churches.append(self._add_church(self.tile['coord']))
        json_write('Data/Elements/Churches.json', self.churches)

    def close_churches(self):
        self.churches = json_read('Data/Elements/Churches.json')
        for ind, church in enumerate(self.churches):
            
            inds = church['indices']
            counter = 0
            for i in range(inds[0] - 1, inds[0] + 2):
                for j in range(inds[1] - 1, inds[1] + 2):
                    if type(self.board[i, j]) == dict:
                        counter += 1
                        
            if counter == 9 and church['is_open'] == True:
                players_in_church = self.churches[ind]['players']
                if len(players_in_church) != 0:
                    player = Player(players_in_church[0])
                    player.add_item("Churches", church)
                    player.write(player.players_list)
                self.churches[ind]['is_open'] = False
        
        json_write('Data/Elements/Churches.json', self.churches)
        
    @property
    def free_churches(self):
        for ind, church in enumerate(self.churches):
            if self.tile['coord'] == church['indices']:
                return [church]
        return []

        
