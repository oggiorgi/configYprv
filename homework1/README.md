                                      Предоставляю домашнюю работу №1 по конфигурационному управлению

                                                           Вариант №16
Задание №1

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
tar. Эмулятор должен работать в режиме GUI.
Ключами командной строки задаются:
• Имя пользователя для показа в приглашении к вводу.
• Путь к архиву виртуальной файловой системы.
• Путь к стартовому скрипту.
Стартовый скрипт служит для начального выполнения заданного списка
команд из файла.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также
следующие команды:
1. touch.
2. chmod.

Все функции эмулятора должны быть покрыты тестами, а для каждой из
поддерживаемых команд необходимо написать 3 теста.


Выполнение
1. Создать проект и установить библиотеки

        npm install
2. Установить нужные пакеты:

        npm install yargs adm-zip fs-extrapath jest

 3. Скачать проект на рабочий стол, должна получится такая иерархия:

4. Для запуска проекта запускаем командную строку, переходим в папку с эмулятором и используем команду

        Ctrl+R cmd - Вызов командной строки Windows.
        node src/emulator.js --config=./config.json

5. Можем пользоваться командами cd ls exit touch chmod

6. Для запуска тестов прописываем команду

        npm test


Для входа в эмулятор

    C:\Users\Георгий>cd G:\Konfig

    C:\Users\Георгий>cd /d G:

    G:\Konfig>py emulator.py virtual_fs.tar

Для проверки тестов

    python -m unittest unittests.py


   

