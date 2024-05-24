from abc import ABC, abstractmethod

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer
from sklearn.svm import SVC

from metrics import calculate_gain


class BaseModel(ABC):
    name: str

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def preprocess_features(self, x: np.ndarray, is_train: bool) -> np.ndarray:
        """
        Preprocess the features before fitting the model.
        """
        return x

    @abstractmethod
    def _fit(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Perform fit.
        :param x: features - n x m array, where n is the number of samples
        :param y: target - n element array
        """

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the model to the data.
        :param x: features
        :param y: target
        """

        x_processed = self.preprocess_features(x, is_train=True)
        self._fit(x_processed, y)

    @abstractmethod
    def _predict(self, x: np.ndarray) -> np.ndarray:
        """
        Predict the target for the given features. Ensure target is a 1D array
        representing probability of positive class for each sample.
        :param x: features
        :return: target
        """

    def calculate_gain(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate the gain of the predictions compared to the ground truth on given
        data.
        :param x: features
        :param y: target
        :return: gain
        """
        x_processed = self.preprocess_features(x, is_train=False)
        y_pred = self._predict(x_processed)

        return calculate_gain(y, y_pred, x.shape[1])


class RandomForest(BaseModel):
    name = "RandomForest"

    def __init__(self, n_estimators: int = 100, max_depth: int | None = None):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
        )

    def _fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(x, y)

    def _predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)[:, 1]


class LDA(BaseModel):
    name = "LDA"

    def __init__(self):
        self.model = LinearDiscriminantAnalysis()

    def _fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(x, y)

    def _predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)[:, 1]


class LDAPolynomial(LDA):
    name = "LDAPolynomial"

    def __init__(self, degree: int = 2, interactions_only: bool = False):
        self.poly = PolynomialFeatures(
            degree=degree, interaction_only=interactions_only
        )
        super().__init__()

    def preprocess_features(self, x: np.ndarray, is_train: bool) -> np.ndarray:
        """
        Convert features to polynomial features.
        """
        if is_train:
            self.poly.fit(x)
        return self.poly.transform(x)


class LDASpline(LDA):
    name = "LDASpline"

    def __init__(self, knots: int = 2, degree: int = 3):
        self.spline = SplineTransformer(n_knots=knots, degree=degree)
        super().__init__()

    def preprocess_features(self, x: np.ndarray, is_train: bool) -> np.ndarray:
        """
        Convert features to spline features.
        """
        if is_train:
            self.spline.fit(x)
        return self.spline.transform(x)


class QDA(BaseModel):
    name = "QDA"

    def __init__(self):
        self.model = QuadraticDiscriminantAnalysis()

    def _fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(x, y)

    def _predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)[:, 1]


class SVM(BaseModel):
    name = "SVM"

    def __init__(self, kernel: str = "rbf", degree: int = 3):
        self.model = SVC(kernel=kernel, degree=degree, probability=True)

    def _fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(x, y)

    def _predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(x)[:, 1]
