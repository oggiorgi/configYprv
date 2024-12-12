import subprocess
import sys
import os

def get_commit_tree(repo_path):
    """Получает дерево коммитов в репозитории."""
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H', '--reverse'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ошибка при получении коммитов: {result.stderr}")

    commits = result.stdout.splitlines()
    commit_links = [(commits[i], commits[i + 1]) for i in range(len(commits) - 1)]
    return commits, commit_links

def generate_graphviz_code(commits, commit_links):
    """Создает код Graphviz для графа зависимостей коммитов."""
    lines = ["digraph G {", "    rankdir=LR;"]

    for commit in commits:
        lines.append(f'    "{commit}" [shape=ellipse];')

    for parent, child in commit_links:
        lines.append(f'    "{parent}" -> "{child}";')

    lines.append("}")
    return "\n".join(lines)

def save_graph(graph_code, output_path):
    """Сохраняет граф в формате PNG."""
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
        raise RuntimeError(f"Ошибка при генерации PNG: {result.stderr}")

    os.remove(dot_file)

def main():
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
        print(f"Граф зависимостей успешно сохранен в {output_path}.png")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
