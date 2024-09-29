import numpy as np
import pylab as plt
from matplotlib.colors import ListedColormap

# Определение цветовых карт
cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])


def plot_surface(X, y, clf):
    # Шаг сетки
    h = 0.2

    # Устанавливаем границы графика
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    # Создаем сетку для контурного графика
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # Предсказание классификатора для каждой точки сетки
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    # Переформатирование массива предсказаний для контурного графика
    Z = Z.reshape(xx.shape)

    # Создание графика
    plt.figure(figsize=(8, 8))

    # Отображение предсказаний
    plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

    # Отображение тренировочных точек
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold)

    # Установка границ графика
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())