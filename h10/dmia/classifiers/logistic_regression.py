import numpy as np
from scipy import sparse


class LogisticRegression:
    def __init__(self):
        # Инициализация весов модели и истории ошибок
        self.w = None
        self.loss_history = None

    def train(self, X, y, learning_rate=1e-3, reg=1e-5, num_iters=100,
              batch_size=200, verbose=False):
        # Добавление колонки из единиц к входным данным для весов смещения
        X = LogisticRegression.append_biases(X)

        # Количество объектов и признаков
        num_train, dim = X.shape

        # Инициализация весов, если они еще не инициализированы
        if self.w is None:
            self.w = np.random.randn(dim) * 0.01

        # История значений функции потерь
        self.loss_history = []

        # Цикл по итерациям обучения
        for it in range(num_iters):
            # Случайный выбор индексов для формирования батча
            indices = np.random.choice(num_train, batch_size)
            X_batch = X[indices, :]
            y_batch = y[indices]

            # Вычисление значения функции потерь и её градиента
            loss, grad_w = self.loss(X_batch, y_batch, reg)
            self.loss_history.append(loss)

            # Обновление весов на основе градиента
            self.w -= learning_rate * grad_w

            # Вывод промежуточных результатов, если требуется
            if verbose and it % 100 == 0:
                print('iteration %d / %d: loss %f' % (it, num_iters, loss))

        return self

    @staticmethod
    def sigmoid(z):
        # Функция сигмоида для приближения вероятности
        return 1.0 / (1.0 + np.exp(-z))

    def predict_proba(self, X, append_bias=False):
        # Прогноз вероятностей принадлежности к классам
        if append_bias:
            X = LogisticRegression.append_biases(X)
        predictions = self.sigmoid(X.dot(self.w.T))
        y_proba = np.vstack([1 - predictions, predictions]).T
        return y_proba

    def predict(self, X):
        # Прогноз классов на основе предсказанных вероятностей
        y_proba = self.predict_proba(X, append_bias=True)
        y_pred = y_proba.argmax(axis=1)
        return y_pred

    def loss(self, X_batch, y_batch, reg):
        # Вычисление значения функции потерь и градиента
        dw = np.zeros_like(self.w)  # Инициализация градиента нулем
        loss = 0
        h = self.sigmoid(X_batch.dot(self.w))
        loss = -np.dot(y_batch, np.log(h)) - np.dot((1 - y_batch), np.log(1.0 - h))
        dw = (h - y_batch) * X_batch
        num_train = X_batch.shape[0]
        loss = loss / num_train
        dw = dw / num_train
        loss += (reg / (2.0 * num_train)) * np.dot(self.w[:-1], self.w[:-1])
        dw[:-1] = dw[:-1] + (reg * self.w[:-1]) / num_train
        return loss, dw

    @staticmethod
    def append_biases(X):
        # Добавление колонки для веса смещения
        return sparse.hstack((X, np.ones(X.shape[0])[:, np.newaxis])).tocsr()