import matplotlib.pyplot as plt 
import numpy as np
import cv2 as cv
from FileActions import json_read, json_write

def place_meeple(image, player_id, action_type):

    if player_id == 0:
        color = (0, 0, 255) 
    else:
        color = (255, 0, 0) 

    # Получение размеров изображения
    height, width = image.shape[:2]

    # Вычисление координат центра изображения
    center_x = int(width / 2)
    center_y = int(height / 2)
    font                   = cv.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (center_x,center_y)
    fontScale              = 1
    fontColor              = color
    thickness              = 5
    lineType               = 2
    
    if action_type == "road":
        text = 'R'
    elif action_type == "church":
        text = 'C'
    elif action_type == "city":
        text = 'T'
    elif action_type == "field":
        text = 'F'
    cv.putText(image, text, 
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType,
        )
    
    return image

def plot_board(board_0):

    # Создаем новое окно для отображения изображений
    plt.figure()
    
    # Карта, по которой мы будем класть миплов
    for i in range(board_0.shape[0]):
        for j in range(board_0.shape[1]):
            if type(board_0[i, j]) == dict:
                
                meeples = json_read('Visualize/meeples.json')
                
                for ind, meeple in enumerate(meeples):
                        
                    if type(meeple['action']) == dict and meeple.get('plotted') == False:
                        
                        if meeple['action']['type'] == 'church':
                            ind_pair = meeple['action']['indices']
                            if ind_pair[0] == i and ind_pair[1] == j:
                                meeples[ind]['plotted'] = True
                                board_0[i, j]['plot_player'] = meeple['player']
                                board_0[i, j]['action_type'] = meeple['action']['type']
                        
                        else:
                            for ind_pair in meeple['action']['indices']:
                                if ind_pair[0] == i and ind_pair[1] == j and meeple['action']['is_open'] == True:
                                    meeples[ind]['plotted'] = True
                                    board_0[i, j]['plot_player'] = meeple['player']
                                    board_0[i, j]['action_type'] = meeple['action']['type']
                                    
                        json_write('Visualize/meeples.json', meeples)
    
    board = board_0
    # Убираем строчки и стобцы с 0-ми с массива досок:
    indices = ~np.all(board_0 == 0, axis=1)
    board = board_0[indices]
    indices2 = ~np.all(board == 0, axis=0)
    board = board[:, indices2]
    
    # Проходим по каждому элементу массива и отображаем изображение
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            
            
            if type(board[i, j]) == dict:
                image_path = board[i, j]['image_path']
                image = cv.imread(image_path)
                if board[i, j].get('rotated') != None:
                    for _ in range(board[i, j]['rotated']):
                        image = cv.rotate(image, cv.ROTATE_90_CLOCKWISE)
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                if board[i, j].get('plot_player') is not None:
                    image = place_meeple(image, board[i, j]['plot_player'], board[i, j]['action_type'])
                
            else:
                image_path = 'Visualize/Tiles/gray.png'
                image = cv.imread(image_path)
                
            
            plt.subplot(board.shape[0], board.shape[1], i * board.shape[1] + j + 1)

            if type(board[i, j]) == dict:
                plt.text(20, 20, f'{board[i, j]["GameID"]}')

            plt.imshow(image)
            
            plt.axis('off')
    plt.savefig('1.png')
