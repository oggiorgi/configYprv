import unittest
from config_to_toml import resolve_value, parse_array, parse_struct, parse_config, generate_toml

class TestConfigToToml(unittest.TestCase):

    def test_resolve_value(self):
        """Тест функции преобразования строки в значение Python."""
        self.assertEqual(resolve_value('"string_value"'), "string_value")
        self.assertEqual(resolve_value("123"), 123)
        self.assertEqual(resolve_value("true"), True)
        self.assertEqual(resolve_value("false"), False)
        self.assertEqual(resolve_value("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(resolve_value("{key1 = true, key2 = false}"), {"key1": True, "key2": False})

    def test_parse_array(self):
        """Тест парсинга массивов."""
        self.assertEqual(parse_array('"value1", "value2", "value3"'), ["value1", "value2", "value3"])
        self.assertEqual(parse_array('1, 2, 3'), [1, 2, 3])
        self.assertEqual(parse_array('{nested = true}, {nested = false}'), [{"nested": True}, {"nested": False}])

    def test_parse_struct(self):
        """Тест парсинга структур."""
        input_struct = "key1 = true, key2 = false, nested = {subkey = 123}, listkey = [1, 2]"
        expected_output = {
            "key1": True,
            "key2": False,
            "nested": {"subkey": 123},
            "listkey": [1, 2],
        }
        self.assertEqual(parse_struct(input_struct), expected_output)

    def test_parse_config(self):
        """Тест парсинга конфигурационного файла."""
        input_data = """
        set app_name = "MyApp";
        struct {
            features = {
                dark_mode = true,
                experimental = false,
                beta_features = ["feature1", "feature2"],
            },
            settings = {
                theme = "dark",
                notifications = {
                    email = true,
                    sms = false,
                },
            },
        }
        """
        expected_result = {
            "app_name": "MyApp",
            "features": {
                "dark_mode": True,
                "experimental": False,
                "beta_features": ["feature1", "feature2"],
            },
            "settings": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "sms": False,
                },
            },
        }
        self.assertEqual(parse_config(input_data), expected_result)

    def test_generate_toml(self):
        """Тест генерации TOML."""
        input_data = {
            "app_name": "MyApp",
            "features": {
                "dark_mode": True,
                "experimental": False,
                "beta_features": ["feature1", "feature2"],
            },
            "settings": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "sms": False,
                },
            },
        }
        expected_toml = """app_name = "MyApp"

[features]
dark_mode = true
experimental = false
beta_features = ["feature1", "feature2"]

[settings]
theme = "dark"

[settings.notifications]
email = true
sms = false"""
        self.assertEqual(generate_toml(input_data).strip(), expected_toml.strip())

if __name__ == '__main__':
    unittest.main()
