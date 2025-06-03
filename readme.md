# Deep learning for robotics
## Neuroevolution of jumping behaviour of a jumping agent

Jump King: AI Edition is a deterministic 2D skill-based platformer where the objective is to reach a goal platform by jumping across a fixed series of intermediate platforms using precise projectile motion. The game is designed for both human players and AI agents trained using NEAT or PPO.

## Objective

The player starts on a ground-level platform on the far left of the screen. The goal is to reach the ground-level platform on the far right, by successfully jumping across suspended intermediate platforms placed at varying heights and horizontal distances.

Falling, jumping outside screen bounds, or touching the ground anywhere else results in a game over and resets the level.

## Controls (Human Player)

- Hold the `SPACE` key: This enters aiming mode. A dotted trajectory arc is shown, oscillating over time to help aim.
- Release the `SPACE` key: The player jumps in the current direction based on the visible arc. The jump power is fixed; only the direction varies.

The game is designed to require precision. There is no air control and no direction change mid-jump. All motion is governed by initial jump direction and projectile physics.

## Game Physics

The player moves according to projectile motion:

- Horizontal and vertical components of velocity are calculated from the aim direction.
- Gravity is applied every frame to the vertical velocity.
- There is no air resistance or friction.

Gravity causes the player to accelerate downwards each frame, resulting in a curved jump arc. The longer the player is airborne, the more downward momentum they accumulate.

To prevent the player from moving too fast and passing through platforms, a fall speed cap is enforced.

## Jump Mechanic

The jump mechanic is based on direction selection with fixed power:

- When the player is on a platform and holds `SPACE`, an oscillating trajectory is shown.
- This arc moves within a rectangular area above and in front of the player.
- When the key is released, the direction at that moment is used to compute the jump vector.
- The jump direction is normalized and scaled by a fixed power value to compute velocity.

## Trajectory Indicator

While aiming, the game displays a dotted arc showing the predicted jump path. This is calculated using the current aim direction and fixed power, with simulated points showing the future path based on projectile motion. This visual aid helps players judge where the jump will land before committing.

## Platforms

- Start and end platforms are at ground level on the left and right ends of the screen, respectively.
- Up to 15 intermediate platforms are placed at various vertical and horizontal positions.
- The platform layout is fixed and designed to allow a continuous, playable jump path.
- Platforms never overlap, and spacing ensures the player always has a reachable next step.

## Collision Detection

- If the player lands on the **top** of a platform while falling downward, they stop, land safely, and can jump again.
- If the player touches the **sides or bottom** of a platform, their horizontal velocity is canceled, and they begin to fall straight down.
- If the player falls off the screen or touches the ground (except the start/end pads), the game resets.

## Scoring

- +1 point is awarded for each successful landing on a new intermediate platform.
- No points are given for landing again on the same platform.
- Reaching the goal can optionally give a larger bonus (e.g., +10).
- Dying resets the score to 0.

## AI Agent Integration

The game supports training AI agents using NEAT or PPO.

### Observation Space

A sample observation vector for the agent might include:

- Player's current position (x, y)
- Player's velocity (vx, vy)
- Relative position to the next platform (dx, dy)

### Action Space

The agent produces a 2D output vector indicating the jump direction (dx, dy), which is normalized and scaled to fixed power.

### Reward Function

- +1 for landing on a new intermediate platform
- +10 for reaching the goal
- -1 to -10 for dying (falling or jumping out of bounds)
- Optional time penalty (e.g., -0.01 per frame) to encourage efficiency

### NEAT Integration

The game can be used with `neat-python`. Each genome controls a player in the environment, receives state observations, outputs actions, and is scored by total reward (fitness).

### PPO Integration

The game can be wrapped as a `gym.Env` and trained using libraries like `stable-baselines3`. The same observation and action spaces apply, allowing continuous control.

## Setup

1. Install Python 3.8+ and Pygame:

