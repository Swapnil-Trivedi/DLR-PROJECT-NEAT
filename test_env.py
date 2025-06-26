from jumpking_env import JumpKingEnv
import time

env = JumpKingEnv(render_mode="human")
obs, _ = env.reset()
done = False

while not done:
    action = env.action_space.sample()
    obs, reward, done, _, _ = env.step(action)
    env.render()
    time.sleep(0.02)

env.close()
