import numpy as np
from random import randrange


def eval_numerical_gradient(f, x):
    """
   Численное приближение градиента функции f в точке x
   - f должна быть функцией, принимающей один аргумент
   - x - точка (numpy массив), в которой вычисляется градиент
    """
    fx = f(x)  # Значение функции в исходной точке
    grad = np.zeros(x.shape)  # Инициализация градиента нулями
    h = 0.00001  # Малое возмущение для приближения производной

    # Итерация по всем индексам в массиве x
    it = np.nditer(x, flags=['multi_index'], op_flags=['readwrite'])
    while not it.finished:
        ix = it.multi_index
        old_value = x[ix]
        x[ix] = old_value + h  # Прибавление h
        fxh = f(x)  # Вычисление f(x + h)
        x[ix] = old_value  # Возврат к исходному значению

        # Вычисление частной производной
        grad[ix] = (fxh - fx) / h  # Наклон
        print(ix, grad[ix])
        it.iternext()  # Переход к следующему измерению

    return grad


def grad_check_sparse(f, x, analytic_grad, num_checks):
    """
   Проверка градиента в случайных позициях
    """
    h = 1e-5  # Малое возмущение

    for i in range(num_checks):
        ix = tuple([randrange(m) for m in x.shape])
        old_value = x[ix]
        x[ix] = old_value + h  # Прибавление h
        fxph = f(x)  # Значение f(x + h)
        x[ix] = old_value - 2 * h  # Вычитание 2h
        fxmh = f(x)  # Значение f(x - h)
        x[ix] = old_value  # Возврат к исходному значению

        # Численное приближение градиента
        grad_numerical = (fxph - fxmh) / (2 * h)
        # Аналитическое значение градиента
        grad_analytic = analytic_grad[ix]
        # Вычисление относительной ошибки
        rel_error = abs(grad_numerical - grad_analytic) / (abs(grad_numerical) + abs(grad_analytic))
        print('numerical: %f analytic: %f, relative error: %e' % (grad_numerical, grad_analytic, rel_error))