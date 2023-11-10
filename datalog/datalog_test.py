from datalog import datalog


@datalog
def cities():
    city(1, 'Москва')
    city(2, 'Санкт-Петербург')
    city(3, 'Новосибирск')
    ordered(1, 1)
    ordered(1, 2)
    ordered(3, 3)
    product(1, 'чай')
    product(2, 'хлеб')
    product(3, 'цветы')
    ship(ProdName, City) <= ordered(CustNo, ProdNo), \
        city(CustNo, City), product(ProdNo, ProdName)


@datalog
def metro():
    links(1, 'ВДНХ', 'Алексеевская')
    links(1, 'Алексеевская', 'Рижская')
    links(1, 'Рижская', 'Проспект Мира')
    links(2, 'Комсомольская', 'Курская')
    links(2, 'Курская', 'Таганская')
    links(2, 'Таганская', 'Павелецкая')
    reach(X, Y) <= links(L, X, Y)
    reach(X, Y) <= links(L, Y, X)
    reach(X, Y) <= reach(X, Z), reach(Z, Y)


@datalog
def feelings():
    person(vasya)
    person(masha)
    loves(vasya, masha)
    loves(X, X) <= person(X)
    one_sided_love(X) <= loves(X, Y), ~loves(Y, X)


print(cities().query('ship("чай", Сity)'))
from pprint import pprint
_, rows = cities().query('ship(ProdName, Сity)')
pprint(rows)
print(metro().query('reach("ВДНХ", Station)'))
print(feelings().query('one_sided_love(Who)'))
