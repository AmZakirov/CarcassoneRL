import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

from Env import Carcassone
from Visualize.Visualizer import plot_board
from Models.DQNagent import DQNAgent


def main():
    
    utility_matrix = np.load('utility.npy')
    num_ep = 10
    rewards = []
    random_rewards = []
    winners = np.array(np.linspace(0, 0, num_ep))
    mean_rewards = np.array(np.linspace(0, 0, num_ep))
    mean_random_rewards = np.array(np.linspace(0, 0, num_ep))
    state_size = 17
    action_size = 4      
    agent = DQNAgent(state_size, action_size, to_load=True)
    
    for episode in range(num_ep):
        
        env = Carcassone()

        for ind, tile in enumerate(env.tiles):
            
            if ind % 2 == 0:
                try:
                    tile_to_put, actions, rewards_ = env.step(tile, 0, utility_matrix, dqn=True)
                except:
                    continue
                
                next_state = env.dqn_state(tile_to_put, actions, rewards_)
                next_state = np.reshape(next_state, [1, state_size])
                if ind != 0:
                    action = agent.act_loaded(next_state)
                else:
                    action = len(actions) - 1
                    
                reward = env.dqn_action(tile_to_put, actions, rewards_, action)
                points = env.end_game()
                        
            else:
                try:
                    env.step(tile, 1, utility_matrix)
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
        
        print('Episode done', episode, datetime.now(), final_rewards)
        
    np.save('rewards_dqn', rewards)
    np.save('winners_dqn', winners)
    plot_board(env.board.board)  
    plt.show()
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