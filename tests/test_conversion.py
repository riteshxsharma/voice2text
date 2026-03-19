import unittest

from voice2text.conversion import convert_transcript


class ConversionTests(unittest.TestCase):
    def test_equation_conversion(self) -> None:
        result = convert_transcript("begin equation alpha equals pi over 2 end equation")
        self.assertEqual(result.latex_text, "\\[\n\\alpha = \\frac{\\pi}{2}\n\\]\n")
        self.assertEqual(result.emacs_text, result.latex_text)


if __name__ == "__main__":
    unittest.main()
