Initial Setup
Integrated NEAT with a Pygame JumpKing environment.

Created eval_genomes to run genomes on a single environment instance, resetting only the player to avoid flickering.

Added player reset logic to speed up training cycles without restarting the whole game.

Fitness Function Tuning
Implemented a composite fitness function rewarding:

Staying in the air (+ small positive reward per step).

Moving horizontally forward.

Landing on new pads (+ significant bonus).

Reaching the goal (+ ultimate reward).

Penalizing dying and going out-of-bounds heavily.

Added rewards for longer and higher jumps to encourage exploration of bigger jumps.

Inputs and Observations
Started with basic player state (position, velocity).

Added next pad center coordinates as inputs to help the agent focus on landing pads.

Normalized all observations to consistent scales for NEAT.

Rendering and Performance
Disabled rendering during training to speed up evolution.

Noticed slow rendering due to Pygame window refresh; switching to no rendering sped training significantly.

NEAT Configuration and Training Adjustments
Increased population size from 50 to 200.

Increased max generations from 50 to 200.

Observed speciation and stable fitness plateau around ~50.4.

Added CSV logging of fitness and statistics per generation.

Created a log directory to store training run outputs cleanly.

Split logging and CSV-writing utilities to keep training script cleaner.

Debugging and Fixes
Fixed missing attributes (e.g., player.vx → corrected to player.x and velocity properties).

Handled exceptions due to missing render or display properties.

Managed environment step and reset correctly to avoid losing state.

Current State and Next Steps
Training runs consistently with no flickering.

Agent starts to explore jumping but fitness plateaus early.

Speciation happens early but populations share similar fitness.

Considering adding more inputs or changing reward balance.

Added fitness logging to monitor trends and dips in fitness values.


-----------------------------------------------------------------------

# Run 3 New Fitness Strategy
Goals:

Encourage constant forward movement (no staying still or moving backward).

Penalize dying or going out-of-bounds.

Reward initiating jumps.

Reward longer jumps (distance traveled in air).

Reward landing on pads and especially reaching the goal.