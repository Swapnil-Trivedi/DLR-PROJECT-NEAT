# NEAT Platformer AI – Evolving Agents for a Jump King-Inspired Game

## 1. Introduction

This project explores how **Neuroevolution**, specifically the **NEAT (Neuroevolution of Augmenting Topologies)** algorithm, can be used to train an AI agent to master a simplified 2D platformer inspired by *Jump King*. The agent learns using evolutionary strategies, evolving neural networks **without backpropagation**.

The goal is to evolve agents that can learn strategic jumping across platforms, navigating physics like gravity and momentum, **without any hardcoded logic or reward shaping**.

---

## 2. Game Architecture

###  Objective
The agent must:
- Start on a fixed platform
- Jump across intermediate pads
- Reach the final goal platform
- Avoid falling or idling

### Mechanics
- **Gravity:** Constant force pulling the agent down
- **Jumping:** Jump angle output by neural net; fixed power
- **Collision:** Detects landing or edge contact with platforms
- **Failure States:** Falling out of bounds or stalling

---

## 3. Neural Network Design

### Inputs to the NEAT Network:
1. `player.x` – Horizontal position  
2. `player.y` – Vertical position  
3. `vel_x` – Horizontal velocity  
4. `vel_y` – Vertical velocity  
5. `dx` – Distance to nearest platform (X-axis)  
6. `dy` – Distance to nearest platform (Y-axis)  

### Output:
- **Jump angle** (mapped from -90° to +90°)  
  Used to compute:
```
dx = cos(angle) * power
dy = sin(angle) * power

```

---

## 4. NEAT Configuration

- **Population Size:** 50 - 150  
- **Activation Function:** `tanh`  `sigmoid` `ReLU`
- **Network Type:** Feedforward  
- **Input/Output:** 6 inputs, 1 output  
- **Speciation:** Enabled  
- **Crossover & Mutation:** Tuned via config  
- **Elitism:** Top genomes preserved per generation  

---

## 5. Fitness Function Design

| Behavior                     | Reward / Penalty |
|-----------------------------|------------------|
| Landing on new pad          | +50              |
| Re-landing same pad         | −10              |
| Reaching goal pad           | +300             |
| Falling / dying             | −20              |
| Forward progress ≥ 50px     | +5               |
| Idling on same pad          | −50              |
| Edge contact (slide)        | +0.2             |
| Time penalty (per frame)    | −0.01            |
| Good jump direction         | +0.5             |

This encourages exploration, planning, and generalization.

---

## 6. Genetic Diversity & Extinction Strategy

### Genocide Logic
- Every 20 seconds: Bottom 65% of agents are culled (unless in top 35%)
- Encourages innovation and prevents overfitting

### Checkpointing
- Saves every 20 generations  
- Best genome stored as `best_genome.pkl` for testing and replay

---

## Training Process

### Key Training Milestones:

**Generations 0–10:**  
- Agents discover basic jumping  
- Frequent failure due to overshooting or poor aim  

**Generations 10–25:**  
- Consistent landings on intermediate pads  
- Smarter, more deliberate jumps emerge  

**Generations 25+:**  
- Agents consistently reach the goal  
- Multi-jump strategies evolve  

---

## 8. Experimentation Summary

### Mutation & Crossover
- Higher mutation rates to promote exploration  
- Adaptive mutation avoids local optima  

### Fitness Tweaks
- Upward-forward motion rewarded  
- Idleness and repetition penalized  

### Environment Tweaks
- Randomized platform layouts  
- Future work: moving platforms, hazards  

---

## 9. Results & Observations

- **Best Genome Fitness:** ~300+  
- **Goal Reached:** ~Generation 12 (with extinction strategy)  
- **Training Time:** Reduced with aggressive extinction  
- **Behavioral Insight:**
- Learned upward-forward jumps toward reachable platforms  
- Adapted to varied layouts – **strong generalization**

---

## 10. Conclusion

This project demonstrates that:
- **NEAT** is effective for training intelligent agents in 2D platformers  
- **Fitness shaping** is crucial for meaningful learning  
- **Genetic extinction** accelerates convergence and avoids stagnation  
- Even with **a single output (jump angle)**, complex strategies can emerge

The trained agent successfully learns to complete the level using strategic, physics-aware jumps — opening doors for future enhancements like dynamic environments or competitive multi-agent evolution.

---

## Demo & Future Work

- Replay saved genomes using `best_genome.pkl`
- Explore co-evolution or adversarial agents
- Add dynamic terrain, moving platforms, or longer levels

---

## Requirements

- Python 3.10+
- `neat-python`
- `pygame` (for visual simulation)
- `numpy`, `math`, etc.

Install with:
```bash
pip install -r requirements.txt
``` 