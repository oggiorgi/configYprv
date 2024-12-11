import unittest
import os
from graphviz_visualizer.visualizer import generate_graphviz_graph

class TestGraphvizVisualizer(unittest.TestCase):

    def test_generate_graphviz_graph(self):
        # Тестовые данные
        commits = ["commit1", "commit2", "commit3"]
        output_path = "test_graph"

        # Генерация графа
        generate_graphviz_graph(commits, output_path)

        # Проверка наличия файла PNG
        self.assertTrue(os.path.exists(output_path + ".png"))

        # Удаление тестовых файлов
        os.remove(output_path + ".png")

if __name__ == "__main__":
    unittest.main()

