"""AST Parser using libclang for C/C++ code analysis"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

# Configure libclang before importing Index
try:
    from clang import cindex
    # Try common library locations in order of preference
    libclang_paths = [
        '/opt/homebrew/opt/llvm/lib/libclang.dylib',  # macOS M1/M2
        '/usr/lib/libclang.dylib',                      # macOS Intel
        '/usr/lib/llvm-11/lib/libclang.so',             # Linux (LLVM 11)
        '/usr/lib/llvm-12/lib/libclang.so',             # Linux (LLVM 12)
        '/usr/lib/llvm-13/lib/libclang.so',             # Linux (LLVM 13)
        '/usr/lib/x86_64-linux-gnu/libclang.so',        # Linux (Debian/Ubuntu)
        '/usr/lib/aarch64-linux-gnu/libclang.so',       # Linux (ARM64/Debian)
    ]
    for path in libclang_paths:
        if os.path.exists(path):
            cindex.conf.set_library_file(path)
            break
except Exception:
    pass  # Use system default

from clang.cindex import CursorKind, Index, TranslationUnit

from gaptrace.models.decision_point import (
    DecisionPoint,
    DecisionType,
    FunctionAnalysis,
    ParseResult,
)


class ASTParser:
    """Parse C/C++ source files using libclang AST"""
    
    # Map clang cursor kinds to DecisionType
    DECISION_TYPE_MAP = {
        CursorKind.IF_STMT: DecisionType.IF_CONDITION,
        CursorKind.SWITCH_STMT: DecisionType.SWITCH_CASE,
        CursorKind.FOR_STMT: DecisionType.LOOP_CONDITION,
        CursorKind.WHILE_STMT: DecisionType.LOOP_CONDITION,
        CursorKind.DO_STMT: DecisionType.LOOP_CONDITION,
        CursorKind.CASE_STMT: DecisionType.SWITCH_CASE,
        CursorKind.DEFAULT_STMT: DecisionType.SWITCH_CASE,
        CursorKind.CALL_EXPR: DecisionType.FUNCTION_CALL,
    }
    
    # Keywords indicating critical code paths
    CRITICAL_KEYWORDS = {
        'nullptr', 'NULL', 'null',
        'throw', 'return -1', 'return 0', 'exit',
        'assert', 'abort', 'FATAL',
        'error', 'fail', 'invalid'
    }
    
    def __init__(self, libclang_path: Optional[str] = None):
        """Initialize AST parser
        
        Args:
            libclang_path: Optional path to libclang library
            
        Raises:
            RuntimeError: If libclang cannot be initialized
        """
        try:
            if libclang_path:
                from clang import cindex
                cindex.conf.set_library_file(libclang_path)
            self.index = Index.create()
        except Exception as e:
            # Provide helpful error message for macOS users
            if 'libclang.dylib' in str(e) or 'libclang.so' in str(e):
                raise RuntimeError(
                    f"libclang not found. Please install LLVM:\n"
                    f"  macOS: brew install llvm\n"
                    f"  Then set: export LLVM_CONFIG_PATH=$(brew --prefix llvm)\n"
                    f"\n"
                    f"  Linux: sudo apt-get install libclang1\n"
                    f"  Windows: Download LLVM from https://github.com/llvm/llvm-project\n"
                    f"\nOriginal error: {e}"
                ) from e
            raise RuntimeError(f"Failed to initialize libclang: {e}") from e
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a C/C++ source file and extract decision points
        
        Args:
            file_path: Path to .cpp or .c file
            
        Returns:
            ParseResult containing all functions and decision points
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Parse translation unit
        try:
            tu = self.index.parse(
                str(file_path),
                options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
            )
        except Exception as e:
            raise RuntimeError(f"Failed to parse {file_path}: {e}")
        
        # Extract functions and decision points
        result = ParseResult(file_path=str(file_path))
        
        for cursor in tu.cursor.get_children():
            if cursor.kind == CursorKind.FUNCTION_DECL:
                self._process_function(cursor, result, str(file_path))
        
        # Update stats
        result.total_decision_points = len(result.all_decision_points())
        result.covered_decision_points = sum(
            1 for dp in result.all_decision_points() if dp.is_covered()
        )
        
        return result
    
    def _process_function(self, cursor, result: ParseResult, file_path: str):
        """Process a function and extract decision points
        
        Args:
            cursor: Clang cursor for function
            result: ParseResult to add function to
            file_path: Path to source file
        """
        func_name = cursor.spelling
        start_line = cursor.location.line
        end_line = cursor.extent.end.line
        
        func_analysis = FunctionAnalysis(
            name=func_name,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line
        )
        
        # Extract decision points from function body
        decision_points = []
        self._extract_decision_points(
            cursor, func_name, file_path, decision_points
        )
        
        func_analysis.decision_points = decision_points
        func_analysis.total_branches = len(decision_points)
        
        result.functions[func_name] = func_analysis
    
    def _extract_decision_points(
        self,
        cursor,
        func_name: str,
        file_path: str,
        decision_points: List[DecisionPoint],
        nesting_level: int = 0
    ):
        """Recursively extract decision points from AST
        
        Args:
            cursor: Current AST cursor
            func_name: Name of enclosing function
            file_path: Path to source file
            decision_points: List to accumulate decision points
            nesting_level: Current nesting depth
        """
        for child in cursor.get_children():
            kind = child.kind
            
            # Handle control flow statements
            if kind == CursorKind.IF_STMT:
                self._extract_if_statement(
                    child, func_name, file_path, decision_points, nesting_level
                )
            elif kind == CursorKind.SWITCH_STMT:
                self._extract_switch_statement(
                    child, func_name, file_path, decision_points, nesting_level
                )
            elif kind in (CursorKind.FOR_STMT, CursorKind.WHILE_STMT, CursorKind.DO_STMT):
                self._extract_loop_statement(
                    child, func_name, file_path, decision_points, nesting_level
                )
            elif kind == CursorKind.CALL_EXPR:
                self._extract_function_call(
                    child, func_name, file_path, decision_points, nesting_level
                )
            
            # Recurse into children
            self._extract_decision_points(
                child, func_name, file_path, decision_points, nesting_level + 1
            )
    
    def _extract_if_statement(
        self,
        cursor,
        func_name: str,
        file_path: str,
        decision_points: List[DecisionPoint],
        nesting_level: int
    ):
        """Extract if/else decision points"""
        condition_text = self._get_condition_text(cursor)
        is_critical = self._is_critical_check(condition_text)
        
        dp = DecisionPoint(
            function_name=func_name,
            decision_type=DecisionType.IF_CONDITION,
            line_number=cursor.location.line,
            condition_text=condition_text,
            file_path=file_path,
            nesting_level=nesting_level,
            is_critical=is_critical
        )
        decision_points.append(dp)
    
    def _extract_switch_statement(
        self,
        cursor,
        func_name: str,
        file_path: str,
        decision_points: List[DecisionPoint],
        nesting_level: int
    ):
        """Extract switch/case decision points"""
        condition_text = self._get_condition_text(cursor)
        
        dp = DecisionPoint(
            function_name=func_name,
            decision_type=DecisionType.SWITCH_CASE,
            line_number=cursor.location.line,
            condition_text=condition_text,
            file_path=file_path,
            nesting_level=nesting_level,
            is_critical=False
        )
        decision_points.append(dp)
    
    def _extract_loop_statement(
        self,
        cursor,
        func_name: str,
        file_path: str,
        decision_points: List[DecisionPoint],
        nesting_level: int
    ):
        """Extract loop decision points"""
        condition_text = self._get_condition_text(cursor)
        
        dp = DecisionPoint(
            function_name=func_name,
            decision_type=DecisionType.LOOP_CONDITION,
            line_number=cursor.location.line,
            condition_text=condition_text,
            file_path=file_path,
            nesting_level=nesting_level,
            is_critical=False
        )
        decision_points.append(dp)
    
    def _extract_function_call(
        self,
        cursor,
        func_name: str,
        file_path: str,
        decision_points: List[DecisionPoint],
        nesting_level: int
    ):
        """Extract function call decision points"""
        call_name = cursor.spelling or "unknown"
        
        # Only track error-handling-like calls
        if any(keyword in call_name.lower() for keyword in ['error', 'check', 'assert', 'throw']):
            dp = DecisionPoint(
                function_name=func_name,
                decision_type=DecisionType.FUNCTION_CALL,
                line_number=cursor.location.line,
                condition_text=call_name,
                file_path=file_path,
                nesting_level=nesting_level,
                is_critical=True
            )
            decision_points.append(dp)
    
    def _get_condition_text(self, cursor) -> str:
        """Extract condition text from cursor
        
        Args:
            cursor: AST cursor
            
        Returns:
            String representation of condition
        """
        try:
            # Get source code for the condition
            extent = cursor.extent
            tokens = list(cursor.get_tokens())
            
            if tokens:
                # Get first few tokens as condition preview
                condition_tokens = []
                for token in tokens[:5]:  # First 5 tokens
                    condition_tokens.append(token.spelling)
                return ' '.join(condition_tokens)
            
            return f"Line {cursor.location.line}"
        except Exception:
            return f"Line {cursor.location.line}"
    
    def _is_critical_check(self, condition_text: str) -> bool:
        """Determine if a condition is critical (null check, error handling)
        
        Args:
            condition_text: The condition source text
            
        Returns:
            True if condition appears to be critical
        """
        lower_text = condition_text.lower()
        
        # Check for null/nullptr checks
        if any(x in lower_text for x in ['null', '!', '==', '!=']):
            return True
        
        # Check for critical keywords
        if any(keyword in condition_text for keyword in self.CRITICAL_KEYWORDS):
            return True
        
        return False


def parse_cpp_file(file_path: str) -> ParseResult:
    """Convenience function to parse a C++ file
    
    Args:
        file_path: Path to .cpp or .c file
        
    Returns:
        ParseResult with all functions and decision points
    """
    parser = ASTParser()
    return parser.parse_file(file_path)


def parse_and_export_json(file_path: str, output_path: Optional[str] = None) -> str:
    """Parse a C++ file and export results as JSON
    
    Args:
        file_path: Path to .cpp or .c file
        output_path: Optional path to write JSON (defaults to same dir as source)
        
    Returns:
        Path to output JSON file
    """
    result = parse_cpp_file(file_path)
    
    if output_path is None:
        output_path = Path(file_path).with_suffix('.gaptrace.json')
    
    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    return str(output_path)
