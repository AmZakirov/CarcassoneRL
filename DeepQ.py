import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt

from Env import Carcassone
from Visualize.Visualizer import plot_board
from Models.DQNagent import DQNAgent

state_size = 17
action_size = 4
output_dir = "Models/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

        
def main():
    
    utility_matrix = np.load('utility.npy')
    num_ep = 50
    rewards = []
    random_rewards = []
    winners = np.array(np.linspace(0, 0, num_ep))
    mean_rewards = np.array(np.linspace(0, 0, num_ep))
    mean_random_rewards = np.array(np.linspace(0, 0, num_ep))
    
    agent = DQNAgent(state_size, action_size)
    
    for episode in range(num_ep):
        
        env = Carcassone()
        last_state = np.reshape(np.linspace(0, 0, state_size), [1, state_size])
        for ind, tile in enumerate(env.tiles):
            
            if ind % 2 == 0:
                try:
                    tile_to_put, actions, rewards_ = env.step(tile, 0, utility_matrix, dqn=True)
                except:
                    continue
                
                next_state = env.dqn_state(tile_to_put, actions, rewards_)
                next_state = np.reshape(next_state, [1, state_size])
                action = agent.act(next_state)

                reward = env.dqn_action(tile_to_put, actions, rewards_, action)
                done = True if ind == len(env.tiles) - 1 else False
                points = env.end_game()
                delta = points[0] + reward ** 2
                agent.remember(last_state, action, delta, next_state, done)
                last_state = next_state
                        
            else:
                try:
                    reward, rotation, tile_id, x, y = env.step(tile, 1, utility_matrix)
                except:
                    continue
                
        if len(agent.memory) > 128:
            agent.train(128)
        elif len(agent.memory) > 64:
            agent.train(64)
        elif len(agent.memory) > 32:
            agent.train(32)
            
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
        
    if episode % 50 == 0:
        agent.save(output_dir + "weights_" + "{:04d}".format(episode) + ".hdf5")
        
    agent.save(output_dir + "finalweights.hdf5")
            
    # plot_board(env.board.board)  
    # plt.show()
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