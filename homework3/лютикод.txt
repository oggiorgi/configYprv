import argparse
import re
import sys
import os


def resolve_value(value, is_inside_struct=False):
    """Преобразование значения из строки в соответствующий тип Python."""
    value = value.strip().rstrip(',')  # Убираем пробелы и лишнюю запятую
    print(f"Resolving value: {value}")  # Для отладки

    # Проверяем различные типы значений
    if value.startswith('"') and value.endswith('"'):  # Строка
        return value.strip('"')
    elif re.match(r'^\d+$', value):  # Целое число
        return int(value)
    elif value.lower() == "true":  # Логическое True
        return True
    elif value.lower() == "false":  # Логическое False
        return False
    elif value.startswith("[") and value.endswith("]"):  # Массив
        return parse_array(value[1:-1])  # Убираем квадратные скобки
    elif value.startswith("{") and value.endswith("}"):  # Словарь (структура)
        return parse_struct(value[1:-1])  # Убираем фигурные скобки
    elif is_inside_struct:  # Простое значение внутри структуры
        return value
    else:
        raise ValueError(f"Некорректное значение: {value}")


def parse_array(array_content):
    """Парсинг массивов (списков) с поддержкой вложенных структур."""
    print(f"Parsing array: {array_content}")  # Для отладки
    parsed_array = []
    buffer = ""
    brace_depth = 0  # Уровень вложенности
    inside_quotes = False

    # Обрабатываем содержимое массива символ за символом
    for char in array_content:
        if char == '"' and brace_depth == 0:  # Начало/конец строки
            inside_quotes = not inside_quotes
            buffer += char
        elif char in '[{' and not inside_quotes:  # Начало вложенной структуры/массива
            brace_depth += 1
            buffer += char
        elif char in ']}' and not inside_quotes:  # Конец вложенной структуры/массива
            brace_depth -= 1
            buffer += char
            if brace_depth == 0:  # Завершение вложенной структуры
                parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))
                buffer = ""
        elif char == ',' and not inside_quotes and brace_depth == 0:  # Разделение элементов
            if buffer.strip():
                parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))
            buffer = ""
        else:
            buffer += char

    # Добавляем последний элемент, если остался
    if buffer.strip():
        parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))

    return parsed_array


def parse_struct(struct_content):
    """Парсинг структур (словарей) с поддержкой вложенности."""
    print(f"Parsing struct: {struct_content}")  # Для отладки
    parsed_struct = {}
    buffer = ""
    brace_depth = 0
    current_key = None
    inside_quotes = False

    # Обрабатываем содержимое структуры символ за символом
    for char in struct_content:
        if char == '"' and brace_depth == 0:  # Обработка строк
            inside_quotes = not inside_quotes
            buffer += char
        elif char in '[{' and not inside_quotes:  # Вложенные структуры
            brace_depth += 1
            buffer += char
        elif char in ']}' and not inside_quotes:
            brace_depth -= 1
            buffer += char
        elif char == '=' and brace_depth == 0 and not inside_quotes:  # Обнаружение ключа
            current_key = buffer.strip()
            buffer = ""
        elif char == ',' and brace_depth == 0 and not inside_quotes:  # Конец пары ключ-значение
            if current_key:
                parsed_struct[current_key] = resolve_value(buffer.strip(), is_inside_struct=True)
                current_key = None
            buffer = ""
        else:
            buffer += char

    # Добавляем последнюю пару ключ-значение
    if buffer.strip():
        if current_key:
            parsed_struct[current_key] = resolve_value(buffer.strip(), is_inside_struct=True)

    return parsed_struct


def parse_config(input_data):
    """Основной процесс парсинга конфигурационного файла."""
    print(f"Parsing config data:\n{input_data}")  # Для отладки
    constants = {}  # Для хранения констант
    result = {}  # Итоговый результат
    lines = input_data.splitlines()
    inside_struct = False  # Флаг для отслеживания начала структуры
    struct_buffer = []  # Для временного хранения строк структуры

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):  # Пропускаем пустые строки и комментарии
            continue

        if line.startswith("set "):  # Объявление константы
            match = re.match(r'set\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+);', line)
            if match:
                key, value = match.groups()
                constants[key] = resolve_value(value.strip())
                print(f"Set constant: {key} = {constants[key]}")  # Для отладки
            else:
                raise SyntaxError(f"Синтаксическая ошибка в строке: {line}")

        elif line.startswith("struct {"):  # Начало структуры
            inside_struct = True
            struct_buffer = []
        elif inside_struct and line == "}":  # Конец структуры
            inside_struct = False
            struct_content = " ".join(struct_buffer)
            parsed_struct = parse_struct(struct_content)
            print(f"Parsed struct: {parsed_struct}")  # Для отладки
            result.update(parsed_struct)
        elif inside_struct:  # Строки внутри структуры
            struct_buffer.append(line)
        else:  # Глобальные ключи
            match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+)', line)
            if match:
                key, value = match.groups()
                result[key.strip()] = resolve_value(value.strip())
                print(f"Set key: {key.strip()} = {result[key.strip()]}")  # Для отладки
            else:
                raise SyntaxError(f"Синтаксическая ошибка в строке: {line}")

    # Добавляем константы в результат
    result.update(constants)

    print(f"Final parsed data: {result}")  # Для отладки
    return result


def generate_toml(parsed_data, indent_level=0):
    """Генерация TOML из разобранных данных."""
    toml_lines = []
    indent = '    ' * indent_level  # Отступы

    for key, value in parsed_data.items():
        if isinstance(value, dict):  # Обработка вложенных словарей
            toml_lines.append(f"{indent}[{key}]")
            toml_lines.append(generate_toml(value, indent_level + 1))
        elif isinstance(value, list):  # Обработка массивов
            array_values = ', '.join(
                f'"{v}"' if isinstance(v, str) else str(v).lower() for v in value
            )
            toml_lines.append(f"{indent}{key} = [{array_values}]")
        elif isinstance(value, str):  # Строки
            toml_lines.append(f'{indent}{key} = "{value}"')
        elif isinstance(value, (int, bool)):  # Числа и логические значения
            toml_lines.append(f"{indent}{key} = {str(value).lower()}")

    return "\n".join(toml_lines)


def main():
    """Точка входа программы."""
    parser = argparse.ArgumentParser(description="Конвертировать конфигурационный язык в TOML")
    parser.add_argument("--input", required=True, help="Путь к входному конфигурационному файлу")
    parser.add_argument("--output", required=True, help="Путь к выходному TOML файлу")
    args = parser.parse_args()

    if not os.path.isfile(args.input):  # Проверка наличия входного файла
        print(f"Ошибка: входной файл '{args.input}' не найден.")
        sys.exit(1)

    try:
        # Читаем входной файл
        with open(args.input, 'r') as infile:
            input_data = infile.read()
            print("Raw input data:\n", input_data)  # Для отладки

        # Парсим данные и генерируем TOML
        parsed_data = parse_config(input_data)
        toml_data = generate_toml(parsed_data)

        # Записываем результат в выходной файл
        with open(args.output, 'w') as outfile:
            outfile.write(toml_data)

        print(f"Конфигурация успешно преобразована и сохранена в {args.output}.")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
