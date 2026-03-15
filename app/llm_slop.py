import vowpalwabbit
import random
import pandas as pd


def init_model(n_actions: int = 4) -> vowpalwabbit.Workspace:
    """
    Initialises a VW contextual bandit model with epsilon-greedy exploration.

    Args:
        n_actions (int): Number of possible actions (e.g. article categories).

    Returns:
        vowpalwabbit.Workspace: The initialised VW model.
    """
    return vowpalwabbit.Workspace(f"--cb_explore {n_actions} --epsilon 0.2", quiet=True)


def format_example(context: dict, action: int = None, cost: float = None, prob: float = None) -> str:
    """
    Formats a context (and optional label) into VW's input string format.
    If action/cost/prob are provided, it's a training example.
    If not, it's a prediction example.

    Args:
        context (dict): Feature dict e.g. {"time_of_day": "morning", "device": "mobile"}
        action (int): The action taken (1-indexed).
        cost (float): The cost observed (negative reward — lower is better).
        prob (float): The probability with which the action was chosen.

    Returns:
        str: A VW-formatted example string.
    """
    features = " ".join(f"{k}={v}" for k, v in context.items())

    if action is not None:
        return f"{action}:{cost}:{prob} | {features}"
    else:
        return f"| {features}"


def train(vw: vowpalwabbit.Workspace, context: dict, action: int, reward: float, prob: float) -> None:
    """
    Trains the model on one observed (context, action, reward) tuple.
    Cost = -reward since VW minimises cost.

    Args:
        vw: The VW model.
        context (dict): The observed context features.
        action (int): The action that was taken (1-indexed).
        reward (float): The reward received (e.g. 1.0 for click, 0.0 for no click).
        prob (float): The probability with which the action was chosen.
    """
    example = format_example(context, action=action, cost=-reward, prob=prob)
    vw.learn(example)


def predict(vw: vowpalwabbit.Workspace, context: dict) -> tuple[int, float]:
    """
    Predicts the best action for a given context by sampling from
    the model's probability distribution over actions.

    Args:
        vw: The VW model.
        context (dict): The observed context features.

    Returns:
        tuple[int, float]: (chosen_action (1-indexed), probability of that action)
    """
    example = format_example(context)
    action_probs = vw.predict(example)

    # sample according to probabilities (exploration)
    [chosen] = random.choices(range(len(action_probs)), weights=action_probs)
    return chosen + 1, action_probs[chosen]  # convert to 1-indexed


# --- Example usage ---
if __name__ == "__main__":
    # Actions: 1=sports, 2=politics, 3=tech, 4=entertainment
    ACTIONS = {1: "sports", 2: "politics", 3: "tech", 4: "entertainment"}

    vw = init_model(n_actions=4)

    # Simulate a stream of users arriving with context
    simulated_users = [
        {"time_of_day": "morning", "device": "mobile",  "true_preference": 3},
        {"time_of_day": "evening", "device": "desktop", "true_preference": 2},
        {"time_of_day": "morning", "device": "tablet",  "true_preference": 1},
        {"time_of_day": "night",   "device": "mobile",  "true_preference": 4},
    ] * 50  # repeat 50x so model can learn

    results = []
    for user in simulated_users:
        context = {"time_of_day": user["time_of_day"], "device": user["device"]}

        # Predict
        action, prob = predict(vw, context)

        # Simulate reward: 1.0 if we matched preference, 0.0 otherwise
        reward = 1.0 if action == user["true_preference"] else 0.0

        # Train on observed reward
        train(vw, context, action, reward, prob)

        results.append({"context": context, "action": ACTIONS[action], "reward": reward})

    # Show last 10 predictions
    df = pd.DataFrame(results).tail(10)
    print(df.to_string(index=False))

    vw.finish()
