# restaurant_recommender.py
# VW contextual bandit: learns which cuisine to recommend per user context

import vowpalwabbit
import random

CUISINES = ["italian", "sushi", "mexican", "indian"]

# Simulated user satisfaction per context — the "ground truth" VW has to discover
SATISFACTION = {
    ("lunch", "low",    "cheap"):    {"italian": 0.8, "sushi": 0.3, "mexican": 0.9, "indian": 0.5},
    ("lunch", "high",   "cheap"):    {"italian": 0.7, "sushi": 0.6, "mexican": 0.8, "indian": 0.7},
    ("dinner", "low",   "expensive"):{"italian": 0.5, "sushi": 0.9, "mexican": 0.4, "indian": 0.6},
    ("dinner", "high",  "expensive"):{"italian": 0.6, "sushi": 0.9, "mexican": 0.5, "indian": 0.8},
}

def get_reward(context: dict, cuisine: str) -> float:
    key = (context["time"], context["hunger"], context["budget"])
    scores = SATISFACTION.get(key, {c: 0.5 for c in CUISINES})
    base = scores.get(cuisine, 0.5)
    return base + random.gauss(0, 0.05)  # add noise so it's not trivial

def to_vw_format(context: dict, chosen: str = None, reward: float = None, prob: float = None) -> str:
    action_idx = CUISINES.index(chosen) + 1 if chosen else None
    cost = -reward if reward is not None else None  # VW minimizes cost

    shared = f"shared |user time={context['time']} hunger={context['hunger']} budget={context['budget']}\n"
    
    actions = ""
    for i, cuisine in enumerate(CUISINES, 1):
        if chosen and cuisine == chosen:
            actions += f"{i}:{cost:.4f}:{prob:.4f} |cuisine name={cuisine}\n"
        else:
            actions += f"|cuisine name={cuisine}\n"
    
    return shared + actions

def predict(vw, context: dict):
    example = to_vw_format(context)
    result = vw.predict(example)
    action_idx, prob = result[0]
    return CUISINES[action_idx - 1], prob

def train(vw, context: dict, chosen: str, reward: float, prob: float):
    example = to_vw_format(context, chosen, reward, prob)
    vw.learn(example)

def run():
    vw = vowpalwabbit.Workspace("--cb_explore 4 --epsilon 0.15 --cb_type mtr --quiet", enable_logging=True)

    contexts = [
        {"time": "lunch",  "hunger": "low",  "budget": "cheap"},
        {"time": "lunch",  "hunger": "high", "budget": "cheap"},
        {"time": "dinner", "hunger": "low",  "budget": "expensive"},
        {"time": "dinner", "hunger": "high", "budget": "expensive"},
    ]

    print(f"{'Round':<8} {'Context':<40} {'Recommended':<12} {'Reward':<8}")
    print("-" * 72)

    total_reward = 0
    for round_num in range(1, 201):
        ctx = random.choice(contexts)
        cuisine, prob = predict(vw, ctx)
        reward = get_reward(ctx, cuisine)
        train(vw, ctx, cuisine, reward, prob)
        total_reward += reward

        if round_num % 20 == 0:
            ctx_str = f"{ctx['time']}/{ctx['hunger']}/{ctx['budget']}"
            print(f"{round_num:<8} {ctx_str:<40} {cuisine:<12} {reward:.3f}")

    print(f"\nAverage reward over 200 rounds: {total_reward / 200:.4f}")
    vw.finish()

if __name__ == "__main__":
    run()
