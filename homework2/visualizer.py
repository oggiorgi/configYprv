import subprocess
import sys
import os

def get_commit_tree(repo_path):
    """
    Получает дерево коммитов в репозитории.

    Аргументы:
        repo_path (str): Путь к репозиторию Git.

    Возвращает:
        tuple: Список коммитов и их связей.

    Исключения:
        RuntimeError: Ошибка выполнения команды `git log`.
    """
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H', '--reverse'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ошибка: {result.stderr}")

    commits = result.stdout.splitlines()
    commit_links = [(commits[i], commits[i + 1]) for i in range(len(commits) - 1)]
    return commits, commit_links

def generate_graphviz_code(commits, commit_links):
    """
    Генерирует код Graphviz для графа коммитов.

    Аргументы:
        commits (list): Список коммитов.
        commit_links (list): Связи между коммитами.

    Возвращает:
        str: Код Graphviz.
    """
    lines = ["digraph G {", "    rankdir=LR;"]

    for commit in commits:
        lines.append(f'    "{commit}" [shape=ellipse];')

    for parent, child in commit_links:
        lines.append(f'    "{parent}" -> "{child}";')

    lines.append("}")
    return "\n".join(lines)

def save_graph(graph_code, output_path):
    """
    Сохраняет граф в PNG.

    Аргументы:
        graph_code (str): Код Graphviz.
        output_path (str): Путь для PNG.

    Исключения:
        RuntimeError: Ошибка генерации PNG.
    """
    dot_file = f"{output_path}.dot"
    with open(dot_file, 'w') as file:
        file.write(graph_code)

    result = subprocess.run(
        ['dot', '-Tpng', dot_file, '-o', output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ошибка: {result.stderr}")

    os.remove(dot_file)

def main():
    """
    Основная функция. Запускает скрипт с аргументами:
        - repo_path: путь к репозиторию.
        - output_path: путь для сохранения PNG.
    """
    if len(sys.argv) != 3:
        print("Использование: python visualizer.py <repo_path> <output_path>")
        sys.exit(1)

    repo_path, output_path = sys.argv[1:3]

    if not os.path.isdir(repo_path):
        print(f"Ошибка: Репозиторий {repo_path} не найден.")
        sys.exit(1)

    try:
        commits, commit_links = get_commit_tree(repo_path)
        graph_code = generate_graphviz_code(commits, commit_links)
        save_graph(graph_code, output_path)
        print(f"Граф успешно сохранен в {output_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
