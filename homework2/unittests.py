import unittest
from unittest.mock import patch, mock_open, call
import subprocess
import os
from graphviz_visualizer import visualizer




class TestVisualizer(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_commit_tree(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['git', '-C', 'fake_repo', 'log', '--pretty=format:%H', '--reverse'],
            returncode=0,
            stdout='commit1\ncommit2\ncommit3',
            stderr=''
        )

        commits, commit_links = visualizer.get_commit_tree('fake_repo')

        self.assertEqual(commits, ['commit1', 'commit2', 'commit3'])
        self.assertEqual(commit_links, [('commit1', 'commit2'), ('commit2', 'commit3')])

    @patch('subprocess.run')
    def test_get_commit_tree_error(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['git', '-C', 'fake_repo', 'log', '--pretty=format:%H', '--reverse'],
            returncode=1,
            stdout='',
            stderr='Error: fake error message'
        )

        with self.assertRaises(RuntimeError) as context:
            visualizer.get_commit_tree('fake_repo')

        self.assertIn('Ошибка при получении коммитов', str(context.exception))

    def test_generate_graphviz_code(self):
        commits = ['commit1', 'commit2', 'commit3']
        commit_links = [('commit1', 'commit2'), ('commit2', 'commit3')]

        expected_output = (
            "digraph G {\n"
            "    rankdir=LR;\n"
            "    \"commit1\" [shape=ellipse];\n"
            "    \"commit2\" [shape=ellipse];\n"
            "    \"commit3\" [shape=ellipse];\n"
            "    \"commit1\" -> \"commit2\";\n"
            "    \"commit2\" -> \"commit3\";\n"
            "}"
        )

        graph_code = visualizer.generate_graphviz_code(commits, commit_links)
        self.assertEqual(graph_code, expected_output)

    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    @patch('os.remove')
    def test_save_graph(self, mock_remove, mock_run, mock_file):
        graph_code = "digraph G {\n    rankdir=LR;\n}"
        output_path = 'output_path.png'
        dot_file = 'output_path.png.dot'

        mock_run.return_value = subprocess.CompletedProcess(
            args=['dot', '-Tpng', dot_file, '-o', output_path],
            returncode=0,
            stdout='',
            stderr=''
        )

        visualizer.save_graph(graph_code, output_path)

        mock_file.assert_called_once_with(dot_file, 'w')
        mock_file().write.assert_called_once_with(graph_code)
        mock_run.assert_called_once_with(['dot', '-Tpng', dot_file, '-o', output_path], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, text=True)
        mock_remove.assert_called_once_with(dot_file)

    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    def test_save_graph_error(self, mock_run, mock_file):
        graph_code = "digraph G {\n    rankdir=LR;\n}"
        output_path = 'output_path.png'
        dot_file = 'output_path.png.dot'

        mock_run.return_value = subprocess.CompletedProcess(
            args=['dot', '-Tpng', dot_file, '-o', output_path],
            returncode=1,
            stdout='',
            stderr='Error: fake error message'
        )

        with self.assertRaises(RuntimeError) as context:
            visualizer.save_graph(graph_code, output_path)

        self.assertIn('Ошибка при генерации PNG', str(context.exception))
        mock_file.assert_called_once_with(dot_file, 'w')
        mock_file().write.assert_called_once_with(graph_code)
        mock_run.assert_called_once_with(['dot', '-Tpng', dot_file, '-o', output_path], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, text=True)


if __name__ == '__main__':
    unittest.main()
