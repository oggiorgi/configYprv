                                      Предоставляю домашнюю работу №2 по конфигурационному управлению

                                                           Вариант №16
Задание №2
Разработать инструмент командной строки для визуализации графа
зависимостей, включая транзитивные зависимости. Сторонние средства для
получения зависимостей использовать нельзя.

Зависимости определяются для git-репозитория. Для описания графа
зависимостей используется представление Graphviz. Визуализатор должен
выводить результат в виде сообщения об успешном выполнении и сохранять граф
в файле формата png.

Построить граф зависимостей для коммитов, в узлах которого содержатся
хеш-значения.

Ключами командной строки задаются:

• Путь к программе для визуализации графов.

• Путь к анализируемому репозиторию.

• Путь к файлу с изображением графа зависимостей.

Все функции визуализатора зависимостей должны быть покрыты тестами.