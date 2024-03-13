from Env import Carcassone
from TD import Mats
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np


def main():
    
    mats = Mats()
    num_ep = 9000
    rewards = []
    random_rewards = []
    
    winners = np.array(np.linspace(0, 0, num_ep))
    mean_rewards = np.array(np.linspace(0, 0, num_ep))
    mean_random_rewards = np.array(np.linspace(0, 0, num_ep))
    
    
    for episode in range(num_ep):
        
        env = Carcassone()
        for ind, tile in enumerate(env.tiles):
            
            if ind % 2 == 0:
                
                try:
                    reward, rotation, tile_id, x, y = env.step(tile, 0, mats.utility_matrix)
                except:
                    continue
                
                if tile_id != 0 and episode > 0:
                    mats.update_utility(rotation, tile_id, reward, x, y, previous)
                    previous = (rotation, tile_id - 1, x, y)
                
                if episode == 0:
                    previous = (rotation, tile_id - 1, x, y)
            
            else:
                try:
                    reward, rotation, tile_id, x, y = env.step(tile, 1, mats.utility_matrix)
                except:
                    continue
            
        final_rewards = env.end_game()
        rewards.append(final_rewards[0])
        random_rewards.append(final_rewards[1])
        mean_rewards[episode] = np.mean(rewards)
        mean_random_rewards[episode] = np.mean(random_rewards)

        if final_rewards[1] > final_rewards[0]:
            winners[episode] = 1
        elif final_rewards[1] == final_rewards[0]:
            winners[episode] = 2
        
        print(episode, datetime.now())
        
    np.save('rewards', rewards)
    np.save('winners', winners)
    np.save('utility', mats.utility_matrix)
    
    plt.title('Mean reward')
    plt.plot(mean_rewards, color='r')
    plt.plot(mean_random_rewards, color='b')
    plt.xlabel('episode')
    plt.ylabel('reward')
    plt.show()
    
    plt.title('Win counts (0-TD, 1-Random, 2-Draw)')
    plt.hist(winners, bins = 20)
    plt.show()        
    
main()
