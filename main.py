from Env import Carcassone

def main():
    env = Carcassone()
    for ind, tile in enumerate(env.tiles):
        
        if ind % 2 == 0:
            env.step(tile, 0)
        else:
            env.step(tile, 1)
    
    env.end_game()
    
main()
