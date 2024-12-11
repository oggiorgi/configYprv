import subprocess
import argparse
import os
from graphviz import Digraph


def get_commit_tree(repo_path):
    """
    Получает список коммитов в репозитории и их зависимости.
    """
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H', '--reverse'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ошибка при получении коммитов: {result.stderr}")

    commits = result.stdout.splitlines()
    return commits


def generate_graphviz_graph(commits, output_path):
    """
    Генерирует граф зависимостей в формате Graphviz и сохраняет в файл.
    """
    graph = Digraph(format='png')
    graph.attr(rankdir='LR')

    previous_commit = None

    for commit in commits:
        graph.node(commit, label=commit[:7], shape='ellipse')
        if previous_commit:
            graph.edge(previous_commit, commit)
        previous_commit = commit

    graph.render(output_path, cleanup=True)


def main():
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description="Инструмент для визуализации графа зависимостей Git-коммитов с использованием Graphviz.")
    parser.add_argument('--visualizer_path', required=True, help="Путь к программе для визуализации Graphviz.")
    parser.add_argument('--repo_path', required=True, help="Путь к анализируемому Git-репозиторию.")
    parser.add_argument('--output_path', required=True, help="Путь к выходному файлу с графом зависимостей.")

    args = parser.parse_args()

    os.environ['PATH'] += os.pathsep + os.path.abspath(args.visualizer_path)

    try:
        commits = get_commit_tree(args.repo_path)
        generate_graphviz_graph(commits, args.output_path)
        print(f"Граф зависимостей успешно сохранён в {args.output_path}.png")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

