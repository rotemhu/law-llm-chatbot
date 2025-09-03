import re
import json
from enum import Enum
from typing import List, Dict, Any, Optional

class ParserError(Exception):
    """Base exception for parser operations"""
    pass

class InvalidDocumentError(ParserError):
    """Exception for invalid document structure"""
    pass

class SectionParsingError(ParserError):
    """Exception for section parsing errors"""
    pass

#utilities for every parser
class LineType(Enum):
        ADDENDUM = 'תוספת'
        PART = 'חלק'
        CHAPTER = 'פרק'
        SIGN = 'סימן'
        SECTION = 'סעיף'
        REGULAR = 'רגיל'
        LAW_NAME = 'שם החוק'
        METADATA='metadata' #מבוא, מקור, שם קודם, חתימות, פרסום

stop_tags = {
    LineType.ADDENDUM : [LineType.ADDENDUM, LineType.PART, LineType.METADATA],
    LineType.PART : [LineType.PART, LineType.ADDENDUM, LineType.METADATA],
    LineType.CHAPTER : [LineType.CHAPTER, LineType.PART, LineType.ADDENDUM, LineType.METADATA],
    LineType.SIGN : [LineType.SIGN, LineType.CHAPTER, LineType.PART, LineType.ADDENDUM, LineType.METADATA],
    LineType.SECTION: [LineType.SECTION, LineType.SIGN, LineType.CHAPTER, LineType.PART, LineType.ADDENDUM, LineType.METADATA],
    LineType.METADATA: [LineType.SECTION, LineType.SIGN, LineType.CHAPTER, LineType.PART, LineType.ADDENDUM]
}
def get_line_type(line: str) -> LineType:
    """
    Determines the type of a line in a legal document.
    
    Args:
        line: The line to analyze
        
    Returns:
        LineType: The classified type of the line
        
    Raises:
        ValueError: If line is None or empty
    """
    if line is None:
        raise ValueError("Line cannot be None")
    
    if not isinstance(line, str):
        raise ValueError("Line must be a string")
    
    # Handle empty lines
    if not line.strip():
        return LineType.REGULAR
    
    try:
        # is heading? (= ** =)
        heading_regex = re.compile(r"^(=+)\s*(.+?)\s*(=+)?$")
        m_head = heading_regex.match(line)
        
        if m_head:
            #determine the heading
            title = m_head.group(2).strip(' =()\{\}')
            headings = [LineType.ADDENDUM, LineType.PART, LineType.CHAPTER, LineType.SIGN]
            for t in headings:
                if t.value in title:
                    return t
        
        #is metadata?
        if line.strip().startswith(('<שם>', '<מקור>', '<מבוא>', '<חתימות>', '<פרסום>', '<שם קודם>', '<מאגר')):
            return LineType.METADATA
        
        #is section?
        section_regex = re.compile(r"^\s*@\s*([\d\w־\-\.]+)\.\s*(.*)$")
        m_section = section_regex.match(line)
        if m_section:
            return LineType.SECTION
        #Default
        return LineType.REGULAR
    
    except re.error as e:
        raise ParserError(f"Regex error while parsing line: {e}")
    except Exception as e:
        raise ParserError(f"Unexpected error while determining line type: {e}")

def get_section_properties(line: str) -> Dict[str, str]:
    """
    Extracts section number and text from a section line.
    
    Args:
        line: The section line to parse (should start with @)
        
    Returns:
        Dict containing 'section_num' and 'section_text'
        
    Raises:
        ValueError: If line is None, empty, or not a valid section line
        SectionParsingError: If regex parsing fails
    """
    if line is None:
        raise ValueError("Line cannot be None")
    
    if not isinstance(line, str):
        raise ValueError("Line must be a string")
    
    if not line.strip():
        raise ValueError("Line cannot be empty")
    
    try:
        section_regex = re.compile(r"^\s*@\s*([\d\w־\-\.]+)\.\s*(.*)$")
        m_section = section_regex.match(line)
        
        if not m_section:
            raise ValueError(f"This is not a valid section line: '{line}'")
        
        sec_num = m_section.group(1).strip()
        sec_rest = m_section.group(2).strip()

        return {'section_num': sec_num, 'section_text': sec_rest}
    
    except re.error as e:
        raise SectionParsingError(f"Regex error while parsing section: {e}")
    except Exception as e:
        if isinstance(e, (ValueError, SectionParsingError)):
            raise
        raise SectionParsingError(f"Unexpected error while parsing section: {e}")

class Parser:
    @staticmethod
    def parse(document: str) -> List[Dict[str, Any]]:
        """
        Parse a single document.
        
        Args:
            document: The document to parse
            
        Returns:
            List of parsed sections/blocks
            
        Raises:
            NotImplementedError: This is an abstract method
        """
        raise NotImplementedError("Subclasses must implement parse method")
    
    @staticmethod
    def parse_many(documents: List[str]) -> List[List[Dict[str, Any]]]:
        """
        Parse multiple documents.
        
        Args:
            documents: List of documents to parse
            
        Returns:
            List of parsing results for each document
            
        Raises:
            ValueError: If documents is None or empty
            ParserError: If parsing fails
        """
        if documents is None:
            raise ValueError("Documents list cannot be None")
        
        if not isinstance(documents, list):
            raise ValueError("Documents must be a list")
        
        if not documents:
            return []
        
        results = []
        failed_docs = []
        
        for i, document in enumerate(documents):
            try:
                res = Parser.parse(document)
                results.append(res)
            except Exception as e:
                failed_docs.append({'index': i, 'error': str(e)})
                continue
        
        if not results and failed_docs:
            raise ParserError(f"Failed to parse any documents. Sample errors: {failed_docs[:3]}")
        
        return results

class WikiSectionParser(Parser):
    @staticmethod
    def parse(document: str) -> List[Dict[str, Any]]:
        """
        Parse a Wiki legal document into structured sections.
        
        Args:
            document: The document text to parse
            
        Returns:
            List of parsed legal sections with metadata
            
        Raises:
            ValueError: If document is None or empty
            InvalidDocumentError: If document structure is invalid
            ParserError: If parsing fails unexpectedly
        """
        if document is None:
            raise ValueError("Document cannot be None")
        
        if not isinstance(document, str):
            raise ValueError("Document must be a string")
        
        if not document.strip():
            raise ValueError("Document cannot be empty")
        
        try:
            result = []

            # extract <name> as law name
            try:
                law_match = re.search(r"<שם>\s*(.+)", document)
                law_name = law_match.group(1).strip() if law_match else None
            except Exception as e:
                raise InvalidDocumentError(f"Failed to extract law name: {e}")

            # Normalize lines
            lines = document.splitlines()

            current_part = None  # חלק
            current_chapter = None   # פרק
            current_sign = None   # סימן
            current_section = None

            #Iterating the lines and divide + concat to chunks
            lineIdx = 0
            while lineIdx < len(lines):
                try:
                    chunk = ''
                    line = lines[lineIdx]
                    line_type = get_line_type(line)

                    #Metadata
                    if(line_type == LineType.METADATA):
                        #Pack all current metadata
                        current_part = 'metadata'
                        current_sign = current_chapter = current_section =  None
                        #building the chunk
                        chunk = line
                        #Next line
                        lineIdx+=1
                        while(lineIdx < len(lines) and get_line_type(lines[lineIdx]) not in stop_tags[LineType.METADATA]):
                            chunk+=lines[lineIdx]
                            lineIdx+=1
                    #ADDENDUM
                    elif(line_type == LineType.ADDENDUM):
                        #Pack all current ADDENDUM
                        current_part = line.strip(' =()\{\}')
                        current_sign = current_chapter = current_section = None
                        #building the chunk - first line
                        chunk = line
                        #Next line
                        lineIdx+=1
                        while(lineIdx < len(lines) and get_line_type(lines[lineIdx]) not in stop_tags[LineType.ADDENDUM]):
                            chunk+=lines[lineIdx]
                            #Next line
                            lineIdx+=1
                    #PART, CHAPTER, SIGN
                    elif(line_type == LineType.PART):
                        current_part = line.strip(' =()\{\}')
                        current_chapter = current_sign = current_section = None
                        lineIdx+=1
                    elif(line_type == LineType.CHAPTER):
                        current_chapter = line.strip(' =()\{\}')
                        current_sign = current_section = None
                        if current_part == 'metadata': current_part = None
                        lineIdx+=1
                    elif(line_type == LineType.SIGN):
                        current_sign = line.strip(' =()\{\}')
                        current_section = None
                        if current_part == 'metadata': current_part = None
                        lineIdx+=1
                    #SECTION
                    elif(line_type == LineType.SECTION):
                        #Determine section type
                        try:
                            prop = get_section_properties(line)
                        except Exception as e:
                            raise SectionParsingError(f"Failed to parse section at line {lineIdx}: {e}")
                        
                        if current_part == 'metadata': current_part = None
                        current_section = prop['section_num']
                        chunk = prop['section_text']
                        #Next line
                        lineIdx+=1
                        while(lineIdx < len(lines) and get_line_type(lines[lineIdx]) not in stop_tags[LineType.SECTION]):
                            chunk+=lines[lineIdx]
                            lineIdx+=1
                    else: #regular line
                        chunk = line
                        lineIdx+=1
                    
                    #Pack
                    block = {
                        'law_name': law_name,
                        'part' : current_part,
                        'chapter' : current_chapter,
                        'sign' : current_sign,
                        'section' : current_section,
                        'text': chunk
                    }
                    #Add to results(with filtering of empty blocks)
                    if chunk and chunk.strip():
                        result.append(block)
                        
                except Exception as e:
                    if isinstance(e, (ValueError, SectionParsingError, InvalidDocumentError)):
                        raise
                    raise ParserError(f"Unexpected error parsing line {lineIdx}: {e}")
            
            if not result:
                raise InvalidDocumentError("No valid content blocks found in document")
            
            #return
            return result
        
        except Exception as e:
            if isinstance(e, (ValueError, InvalidDocumentError, SectionParsingError, ParserError)):
                raise
            raise ParserError(f"Unexpected error during document parsing: {e}")
    @staticmethod
    def parse_many(documents: List[str]) -> List[List[Dict[str, Any]]]:
        """
        Parse multiple Wiki legal documents.
        
        Args:
            documents: List of document strings to parse
            
        Returns:
            List of parsing results for each document
            
        Raises:
            ValueError: If documents is None or not a list
            ParserError: If parsing fails
        """
        if documents is None:
            raise ValueError("Documents list cannot be None")
        
        if not isinstance(documents, list):
            raise ValueError("Documents must be a list")
        
        if not documents:
            return []
        
        results = []
        failed_docs = []
        
        for i, document in enumerate(documents):
            try:
                res = WikiSectionParser.parse(document)
                results.append(res)
            except Exception as e:
                failed_docs.append({'index': i, 'error': str(e)})
                continue
        
        if not results and failed_docs:
            raise ParserError(f"Failed to parse any documents. Sample errors: {failed_docs[:3]}")
        
        return results
       
class DoclingParser(Parser):
    pass

class JsonParser(Parser):
    pass
