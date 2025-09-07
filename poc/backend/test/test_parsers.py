import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers import (
    WikiSectionParser, Parser, LineType, 
    get_line_type, get_section_properties,
    ParserError, InvalidDocumentError, SectionParsingError
)


class TestLineType(unittest.TestCase):
    
    def test_get_line_type_section(self):
        line = "@ 1. כל אדם זכאי לבטיחות."
        result = get_line_type(line)
        self.assertEqual(result, LineType.SECTION)
    
    def test_get_line_type_section_with_complex_numbering(self):
        line = "@ 1א. הוראות מיוחדות."
        result = get_line_type(line)
        self.assertEqual(result, LineType.SECTION)
    
    def test_get_line_type_part(self):
        line = "== חלק א' - הוראות כלליות =="
        result = get_line_type(line)
        self.assertEqual(result, LineType.PART)
    
    def test_get_line_type_chapter(self):
        line = "= פרק ראשון - הגדרות ="
        result = get_line_type(line)
        self.assertEqual(result, LineType.CHAPTER)
    
    def test_get_line_type_sign(self):
        line = "=== סימן א' - כללי ==="
        result = get_line_type(line)
        self.assertEqual(result, LineType.SIGN)
    
    def test_get_line_type_addendum(self):
        line = "== תוספת ראשונה =="
        result = get_line_type(line)
        self.assertEqual(result, LineType.ADDENDUM)
    
    def test_get_line_type_metadata(self):
        test_cases = [
            "<שם>חוק הבטיחות</שם>",
            "<מקור>ספר החוקים הפתוח</מקור>",
            "<מבוא>הסבר כללי</מבוא>",
            "<חתימות>חתימת השר</חתימות>",
            "<פרסום>תאריך פרסום</פרסום>"
        ]
        
        for line in test_cases:
            with self.subTest(line=line):
                result = get_line_type(line)
                self.assertEqual(result, LineType.METADATA)
    
    def test_get_line_type_regular(self):
        line = "זהו טקסט רגיל של חוק."
        result = get_line_type(line)
        self.assertEqual(result, LineType.REGULAR)
    
    def test_get_line_type_empty_line(self):
        result = get_line_type("")
        self.assertEqual(result, LineType.REGULAR)
        
        result = get_line_type("   ")
        self.assertEqual(result, LineType.REGULAR)
    
    def test_get_line_type_none_input(self):
        with self.assertRaises(ValueError) as context:
            get_line_type(None)
        self.assertIn("Line cannot be None", str(context.exception))
    
    def test_get_line_type_non_string_input(self):
        with self.assertRaises(ValueError) as context:
            get_line_type(123)
        self.assertIn("Line must be a string", str(context.exception))


class TestGetSectionProperties(unittest.TestCase):
    
    def test_get_section_properties_simple(self):
        line = "@ 1. כל אדם זכאי לבטיחות."
        result = get_section_properties(line)
        
        self.assertEqual(result['section_num'], '1')
        self.assertEqual(result['section_text'], 'כל אדם זכאי לבטיחות.')
    
    def test_get_section_properties_complex_numbering(self):
        line = "@ 15א. הוראות מיוחדות לנושא זה."
        result = get_section_properties(line)
        
        self.assertEqual(result['section_num'], '15א')
        self.assertEqual(result['section_text'], 'הוראות מיוחדות לנושא זה.')
    
    def test_get_section_properties_with_dashes(self):
        line = "@ 1-2. סעיף משולב."
        result = get_section_properties(line)
        
        self.assertEqual(result['section_num'], '1-2')
        self.assertEqual(result['section_text'], 'סעיף משולב.')
    
    def test_get_section_properties_empty_text(self):
        line = "@ 1. "
        result = get_section_properties(line)
        
        self.assertEqual(result['section_num'], '1')
        self.assertEqual(result['section_text'], '')
    
    def test_get_section_properties_invalid_line(self):
        line = "זהו לא סעיף"
        
        with self.assertRaises(ValueError) as context:
            get_section_properties(line)
        self.assertIn("This is not a valid section line", str(context.exception))
    
    def test_get_section_properties_none_input(self):
        with self.assertRaises(ValueError) as context:
            get_section_properties(None)
        self.assertIn("Line cannot be None", str(context.exception))
    
    def test_get_section_properties_empty_input(self):
        with self.assertRaises(ValueError) as context:
            get_section_properties("")
        self.assertIn("Line cannot be empty", str(context.exception))
    
    def test_get_section_properties_non_string_input(self):
        with self.assertRaises(ValueError) as context:
            get_section_properties(123)
        self.assertIn("Line must be a string", str(context.exception))


class TestParser(unittest.TestCase):
    
    def test_parse_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            Parser.parse("test document")
    
    def test_parse_many_empty_list(self):
        result = Parser.parse_many([])
        self.assertEqual(result, [])
    
    def test_parse_many_none_input(self):
        with self.assertRaises(ValueError) as context:
            Parser.parse_many(None)
        self.assertIn("Documents list cannot be None", str(context.exception))
    
    def test_parse_many_non_list_input(self):
        with self.assertRaises(ValueError) as context:
            Parser.parse_many("not a list")
        self.assertIn("Documents must be a list", str(context.exception))


class TestWikiSectionParser(unittest.TestCase):
    
    def setUp(self):
        self.sample_document = """<שם>חוק הבטיחות</שם>
<מקור>ספר החוקים הפתוח</מקור>

= חלק א' - הוראות כלליות =

== פרק ראשון - הגדרות ==

@ 1. בחוק זה, "בטיחות" - אמצעי הגנה על החיים.

@ 2. "רשות" - רשות מוסמכת לפי חוק זה.

== פרק שני - יישום ==

@ 3. הרשות תפעל למען הבטיחות.

= חלק ב' - הוראות מיוחדות =

@ 4. הוראות מיוחדות יחולו במקרים חריגים.

<פרסום>נפרסם בירחון רשמי</פרסום>"""

        self.minimal_document = """<שם>חוק פשוט</שם>
@ 1. סעיף יחיד."""

    def test_parse_success(self):
        result = WikiSectionParser.parse(self.sample_document)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        first_block = result[0]
        self.assertIn('law_name', first_block)
        self.assertIn('part', first_block)
        self.assertIn('chapter', first_block)
        self.assertIn('sign', first_block)
        self.assertIn('section', first_block)
        self.assertIn('text', first_block)
        
        self.assertEqual(first_block['law_name'], 'חוק הבטיחות')

    def test_parse_minimal_document(self):
        result = WikiSectionParser.parse(self.minimal_document)
        
        self.assertGreater(len(result), 0)
        section_block = None
        for block in result:
            if block['section'] == '1':
                section_block = block
                break
        
        self.assertIsNotNone(section_block)
        self.assertEqual(section_block['law_name'], 'חוק פשוט')
        self.assertEqual(section_block['section'], '1')
        self.assertEqual(section_block['text'], 'סעיף יחיד.')

    def test_parse_document_with_sections(self):
        result = WikiSectionParser.parse(self.sample_document)
        
        sections = [block for block in result if block['section'] is not None]
        self.assertGreater(len(sections), 0)
        
        section_1 = next((block for block in sections if block['section'] == '1'), None)
        self.assertIsNotNone(section_1)
        self.assertEqual(section_1['part'], '= חלק א\' - הוראות כלליות =')
        self.assertEqual(section_1['chapter'], '== פרק ראשון - הגדרות ==')

    def test_parse_document_with_metadata(self):
        result = WikiSectionParser.parse(self.sample_document)
        
        metadata_blocks = [block for block in result if block['part'] == 'metadata']
        self.assertGreater(len(metadata_blocks), 0)

    def test_parse_none_document(self):
        with self.assertRaises(ValueError) as context:
            WikiSectionParser.parse(None)
        self.assertIn("Document cannot be None", str(context.exception))

    def test_parse_empty_document(self):
        with self.assertRaises(ValueError) as context:
            WikiSectionParser.parse("")
        self.assertIn("Document cannot be empty", str(context.exception))

    def test_parse_non_string_document(self):
        with self.assertRaises(ValueError) as context:
            WikiSectionParser.parse(123)
        self.assertIn("Document must be a string", str(context.exception))

    def test_parse_document_no_law_name(self):
        document = """@ 1. סעיף ללא שם חוק."""
        
        result = WikiSectionParser.parse(document)
        self.assertGreater(len(result), 0)
        self.assertIsNone(result[0]['law_name'])

    def test_parse_document_no_valid_content(self):
        document = """
        
        
        """
        
        with self.assertRaises(InvalidDocumentError) as context:
            WikiSectionParser.parse(document)
        self.assertIn("No valid content blocks found", str(context.exception))

    def test_parse_hierarchical_structure(self):
        document = """<שם>חוק מבנה</שם>
= חלק א' =
== פרק ראשון ==
=== סימן א' ===
@ 1. סעיף ראשון.
@ 2. סעיף שני.
=== סימן ב' ===
@ 3. סעיף שלישי."""
        
        result = WikiSectionParser.parse(document)
        
        section_1 = next((block for block in result if block['section'] == '1'), None)
        section_3 = next((block for block in result if block['section'] == '3'), None)
        
        self.assertIsNotNone(section_1)
        self.assertIsNotNone(section_3)
        
        self.assertEqual(section_1['sign'], '=== סימן א\' ===')
        self.assertEqual(section_3['sign'], '=== סימן ב\' ===')

    def test_parse_many_success(self):
        documents = [self.minimal_document, self.sample_document]
        
        result = WikiSectionParser.parse_many(documents)
        
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], list)
        self.assertIsInstance(result[1], list)

    def test_parse_many_empty_list(self):
        result = WikiSectionParser.parse_many([])
        self.assertEqual(result, [])

    def test_parse_many_none_input(self):
        with self.assertRaises(ValueError) as context:
            WikiSectionParser.parse_many(None)
        self.assertIn("Documents list cannot be None", str(context.exception))

    def test_parse_many_non_list_input(self):
        with self.assertRaises(ValueError) as context:
            WikiSectionParser.parse_many("not a list")
        self.assertIn("Documents must be a list", str(context.exception))

    def test_parse_many_partial_failure(self):
        documents = [self.minimal_document, "", self.sample_document]
        
        result = WikiSectionParser.parse_many(documents)
        
        self.assertEqual(len(result), 2)

    def test_parse_many_complete_failure(self):
        documents = ["", "   ", None]
        
        with self.assertRaises(ParserError) as context:
            WikiSectionParser.parse_many(documents)
        self.assertIn("Failed to parse any documents", str(context.exception))

    @patch('parsers.get_line_type')
    def test_parse_line_type_error(self, mock_get_line_type):
        mock_get_line_type.side_effect = Exception("Line type error")
        
        with self.assertRaises(ParserError) as context:
            WikiSectionParser.parse("@ 1. test")
        self.assertIn("Unexpected error parsing line", str(context.exception))

    @patch('parsers.get_section_properties')
    def test_parse_section_properties_error(self, mock_get_section_properties):
        mock_get_section_properties.side_effect = Exception("Section parse error")
        
        with self.assertRaises(SectionParsingError) as context:
            WikiSectionParser.parse("@ 1. test")
        self.assertIn("Failed to parse section at line", str(context.exception))


if __name__ == '__main__':
    unittest.main()