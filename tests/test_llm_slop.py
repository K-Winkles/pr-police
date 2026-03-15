import unittest
import vowpalwabbit
from app.llm_slop import init_model, format_example, train, predict

class TestLlmSlop(unittest.TestCase):
    def test_init_model(self):
        model = init_model()
        self.assertIsInstance(model, vowpalwabbit.Workspace)

    def test_format_example(self):
        example = format_example({"time_of_day": "morning", "device": "mobile"}, action=1, cost=-0.5, prob=0.8)
        self.assertEqual(example, "1:-0.5:0.8 | time_of_day=morning device=mobile")

    def test_train(self):
        vw = init_model()
        context = {"time_of_day": "morning", "device": "mobile"}
        train(vw, context, action=1, reward=0.5, prob=0.8)
        action, prob = predict(vw, context)
        self.assertTrue(1 <= action <= 4)
        self.assertTrue(0 <= prob <= 1)


    def test_predict(self):
        vw = init_model()
        context = {"time_of_day": "morning", "device": "mobile"}
        action, prob = predict(vw, context)
        self.assertTrue(1 <= action <= 4)
        self.assertTrue(0 <= prob <= 1)

if __name__ == "__main__":
    unittest.main()