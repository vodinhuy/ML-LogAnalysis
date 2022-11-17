import pickle
from . import logproc

labels = {0: 'Anomalous', 1: 'Normal'}


class LogCLF:
    def __init__(self) -> None:
        self.model = None

    def load_model(self, model_fp):
        with open(model_fp, 'rb') as f:
            self.model = pickle.load(f)

    def _predict_test(self, test) -> int:
        return self.model.predict([test])

    def classify(self, log_item: str) -> str:
        test_inp = logproc.get_input_test(log_item)
        if not test_inp:
            return ""
        ans = self._predict_test(test_inp)
        return labels.get(ans[0])
