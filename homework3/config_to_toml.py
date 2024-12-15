import argparse
import re
import sys
import os

def resolve_value(value, is_inside_struct=False):
    """Преобразование строки в соответствующее значение Python (int, bool, list, dict, str)."""
    value = value.strip().rstrip(',')

    # Определение типа значения по содержимому строки
    if value.startswith('"') and value.endswith('"'):  # Строка
        return value.strip('"')
    elif re.match(r'^\d+$', value):  # Целое число
        return int(value)
    elif value.lower() == "true":  # Логическое значение True
        return True
    elif value.lower() == "false":  # Логическое значение False
        return False
    elif value.startswith("[") and value.endswith("]"):  # Массив
        return parse_array(value[1:-1])
    elif value.startswith("{") and value.endswith("}"):  # Словарь
        return parse_struct(value[1:-1])
    elif is_inside_struct:  # Обработка значения в структуре
        return value
    else:
        raise ValueError(f"Некорректное значение: {value}")

def parse_array(array_content):
    """Парсинг массива (списка), поддерживает вложенные структуры."""
    parsed_array = []
    buffer = ""
    brace_depth = 0  # Уровень вложенности скобок
    inside_quotes = False

    for char in array_content:
        if char == '"' and brace_depth == 0:  # Обработка кавычек
            inside_quotes = not inside_quotes
            buffer += char
        elif char in '[{' and not inside_quotes:  # Увеличиваем вложенность
            brace_depth += 1
            buffer += char
        elif char in ']}' and not inside_quotes:  # Уменьшаем вложенность
            brace_depth -= 1
            buffer += char
            if brace_depth == 0:  # Завершаем элемент массива
                parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))
                buffer = ""
        elif char == ',' and not inside_quotes and brace_depth == 0:  # Разделитель элементов массива
            if buffer.strip():
                parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))
            buffer = ""
        else:
            buffer += char

    # Добавляем последний элемент массива
    if buffer.strip():
        parsed_array.append(resolve_value(buffer.strip(), is_inside_struct=True))

    return parsed_array

def parse_struct(struct_content):
    """Парсинг структуры (словаря), поддерживает вложенные структуры."""
    parsed_struct = {}
    buffer = ""
    brace_depth = 0
    current_key = None  # Текущий ключ словаря
    inside_quotes = False

    for char in struct_content:
        if char == '"' and brace_depth == 0:  # Обработка кавычек
            inside_quotes = not inside_quotes
            buffer += char
        elif char in '[{' and not inside_quotes:  # Увеличиваем вложенность
            brace_depth += 1
            buffer += char
        elif char in ']}' and not inside_quotes:  # Уменьшаем вложенность
            brace_depth -= 1
            buffer += char
        elif char == '=' and brace_depth == 0 and not inside_quotes:  # Разделитель ключ-значение
            current_key = buffer.strip()
            buffer = ""
        elif char == ',' and brace_depth == 0 and not inside_quotes:  # Разделитель элементов словаря
            if current_key:
                parsed_struct[current_key] = resolve_value(buffer.strip(), is_inside_struct=True)
                current_key = None
            buffer = ""
        else:
            buffer += char

    # Добавляем последний элемент словаря
    if buffer.strip() and current_key:
        parsed_struct[current_key] = resolve_value(buffer.strip(), is_inside_struct=True)

    return parsed_struct

def parse_config(input_data):
    """Основной процесс парсинга конфигурационного файла."""
    constants = {}  # Константы, задаваемые через `set`
    result = {}  # Итоговая структура данных
    lines = input_data.splitlines()
    inside_struct = False  # Флаг для обработки блока `struct`
    struct_buffer = []

    for line in lines:
        line = line.strip()

        # Игнорируем пустые строки и комментарии
        if not line or line.startswith("#"):
            continue

        if line.startswith("set "):  # Обработка констант
            match = re.match(r'set\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+);', line)
            if match:
                key, value = match.groups()
                constants[key] = resolve_value(value.strip())
            else:
                raise SyntaxError(f"Синтаксическая ошибка в строке: {line}")

        elif line.startswith("struct {"):  # Начало блока `struct`
            inside_struct = True
            struct_buffer = []
        elif inside_struct and line == "}":  # Конец блока `struct`
            inside_struct = False
            struct_content = " ".join(struct_buffer)
            parsed_struct = parse_struct(struct_content)
            result.update(parsed_struct)
        elif inside_struct:  # Сбор строк блока `struct`
            struct_buffer.append(line)
        else:  # Прочие ключи-значения
            match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.+)', line)
            if match:
                key, value = match.groups()
                result[key.strip()] = resolve_value(value.strip())
            else:
                raise SyntaxError(f"Синтаксическая ошибка в строке: {line}")

    result.update(constants)
    return result

def generate_toml(parsed_data, parent_key=None):
    """Генерация TOML файла из словаря."""
    toml_lines = []
    child_sections = []  # Вложенные секции

    for key, value in parsed_data.items():
        if isinstance(value, dict):  # Вложенные словари
            section_name = f"{parent_key}.{key}" if parent_key else key
            child_sections.append((section_name, value))
        elif isinstance(value, list):  # Массивы
            array_values = ', '.join(
                f'"{v}"' if isinstance(v, str) else str(v).lower() for v in value
            )
            toml_lines.append(f"{key} = [{array_values}]")
        elif isinstance(value, str):  # Строки
            toml_lines.append(f'{key} = "{value}"')
        elif isinstance(value, (int, bool)):  # Логические и числовые значения
            toml_lines.append(f"{key} = {str(value).lower()}")

    for i, (section_name, child_data) in enumerate(child_sections):
        if toml_lines or i > 0:  # Пустая строка перед секцией
            toml_lines.append("")
        toml_lines.append(f"[{section_name}]")
        toml_lines.append(generate_toml(child_data, section_name))

    return "\n".join(toml_lines)

def main():
    """Точка входа программы."""
    parser = argparse.ArgumentParser(description="Конвертировать конфигурацию в TOML")
    parser.add_argument("--input", required=True, help="Путь к входному файлу конфигурации")
    parser.add_argument("--output", required=True, help="Путь к выходному файлу TOML")
    args = parser.parse_args()

    if not os.path.isfile(args.input):  # Проверка входного файла
        print(f"Ошибка: входной файл '{args.input}' не найден.")
        sys.exit(1)

    try:
        with open(args.input, 'r') as infile:
            input_data = infile.read()

        parsed_data = parse_config(input_data)
        toml_data = generate_toml(parsed_data)

        with open(args.output, 'w') as outfile:
            outfile.write(toml_data)

        print(f"Конфигурация успешно преобразована и сохранена в {args.output}.")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
