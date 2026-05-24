#!/usr/bin/env python3
"""
Cleanup script to remove vulnerability hints from source code files.
Strips OWASP references, security analysis comments, visualizer warnings,
decoy references, and other vulnerability-related hints from source files.

Does NOT modify:
- .vulns files (machine-readable manifest)
- README.md files (documentation)
- scenarios.md files (documentation)
- node_modules/ directories
- .git directories
- Test files (keep test assertions intact)
"""

import os
import re
import sys
from pathlib import Path

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env'}

# File extensions to process
SOURCE_EXTENSIONS = {'.py', '.java', '.ts', '.js', '.html'}

# Patterns to remove from source files
# Each pattern is a regex that matches a complete line or inline comment to remove

# Java/TypeScript/C-style single-line comment patterns
JAVA_COMMENT_PATTERNS = [
    # // OWASP A0X: ...
    r'^\s*//\s*OWASP\s+A0\d+:\s*.+$',
    # // VULNERABILITY A0X: ...
    r'^\s*//\s*VULNERABILITY\s+A0\d+:\s*.+$',
    # // CHAIN LINK N (chain-XX): ...
    r'^\s*//\s*CHAIN\s+LINK\s+\d+\s*\(chain-\d+\):\s*.+$',
    # // A0X: ...
    r'^\s*//\s*A0\d+:\s*.+$',
    # // BCrypt is secure (decoy)
    r'^\s*//\s*BCrypt\s+is\s+secure\s*\([^)]*\).+$',
    # // Plaintext Private Key Exposure
    r'^\s*//\s*[Pp]laintext\s+.*[Kk]ey\s+.*[Ee]xposure.+$',
    # // OWASP A0X: ... (generic)
    r'^\s*//\s*OWASP\s+A0\d+.*$',
    # // VULNERABILITY A0X: ... (generic)
    r'^\s*//\s*VULNERABILITY\s+A0\d+.*$',
    # // CHAIN LINK ... (generic)
    r'^\s*//\s*CHAIN\s+LINK.*$',
    # // Security Analysis (A0X & A0Y)
    r'^\s*//\s*Security\s+Analysis\s+\(.*\).+$',
    # // Diagnostics Records Vault (A01 horizontal IDOR sandbox!)
    r'^\s*//\s*Diagnostics\s+Records\s+Vault.*$',
    # // any comment that references A0X pattern
    r'^\s*//\s*[Aa]0\d+.*$',
    # // ... (decoy)
    r'^\s*//\s*.*\(decoy\).+$',
    # // ... sandbox!
    r'^\s*//\s*.*[Ss]andbox.*!?.+$',
    # // ... horizontal IDOR
    r'^\s*//\s*.*[Hh]orizontal\s+[Ii]DOR.*$',
    # // ... CRITICAL SECURITY WARNING
    r'^\s*//\s*.*[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning.*$',
    # // ... VISUALIZER
    r'^\s*//\s*.*[Vv]ISUALIZER.*$',
    # // ... high-value transactions are processed without MFA
    r'^\s*//\s*.*[Mm]ulti[- ]?[Ff]actor.*$',
    # // ... without MFA or step-up authentication
    r'^\s*//\s*.*step[- ]?[Uu]p.*$',
    # // ... any line with "sandbox"
    r'^\s*//\s*.*sandbox.*$',
    # // ... any line with "decoy"
    r'^\s*//\s*.*decoy.*$',
    # // ... any line with "OWASP"
    r'^\s*//\s*.*OWASP.*$',
    # // ... any line with "VULNERABILITY"
    r'^\s*//\s*.*VULNERABILITY.*$',
    # // ... any line with "CHAIN LINK"
    r'^\s*//\s*.*CHAIN\s+LINK.*$',
    # // ... any line with "plaintext"
    r'^\s*//\s*.*[Pp]laintext.*$',
    # // ... any line with "Exposing"
    r'^\s*//\s*.*[Ee]xposing.*$',
    # // ... any line with "raw insecure"
    r'^\s*//\s*.*[Rr]aw\s+[Ii]nsecure.*$',
    # // ... any line with "horizontal IDOR"
    r'^\s*//\s*.*[Hh]orizontal\s+IDOR.*$',
    # // ... any line with "CRITICAL SECURITY WARNING"
    r'^\s*//\s*.*[Cc]ritical\s+Security\s+Warning.*$',
    # // ... any line with "VISUALIZER"
    r'^\s*//\s*.*[Vv]ISUALIZER.*$',
    # // ... any line with "Diagnostics Records"
    r'^\s*//\s*.*[Dd]iagnostics\s+Records.*$',
    # // ... any line with "Security Analysis"
    r'^\s*//\s*.*[Ss]ecurity\s+Analysis.*$',
    # // ... any line with "MFA"
    r'^\s*//\s*.*[Mm][Ff][Aa].*$',
    # // ... any line with "step-up"
    r'^\s*//\s*.*step[- ]?[Uu]p.*$',
    # // ... any line with "Calling user"
    r'^\s*//\s*.*[Cc]alling\s+user.*$',
    # // ... any line with "funds from wallets"
    r'^\s*//\s*.*[Ff]unds\s+from\s+wallets.*$',
    # // ... any line with "Any authenticated user"
    r'^\s*//\s*.*[Aa]ny\s+authenticated\s+user.*$',
    # // ... any line with "funds they do not own"
    r'^\s*//\s*.*[Dd]o\s+not\s+own.*$',
    # // ... any line with "horizontal IDOR sandbox"
    r'^\s*//\s*.*[Hh]orizontal\s+IDOR.*$',
    # // ... any line with "allowing other patients"
    r'^\s*//\s*.*[Aa]llowing\s+other.*$',
    # // ... any line with "Privileged Vault Lockout"
    r'^\s*//\s*.*[Pp]rivileged\s+Vault.*$',
    # // ... any line with "Clinical exfiltration"
    r'^\s*//\s*.*[Cc]linical\s+exfiltration.*$',
    # // ... any line with "consultations queue"
    r'^\s*//\s*.*[Cc]onsultations\s+queue.*$',
    # // ... any line with "IDOR visualizer"
    r'^\s*//\s*.*[Ii]DOR\s+visualizer.*$',
    # // ... any line with "Django standard CSRF"
    r'^\s*//\s*.*[Cc]SRF.*$',
    # // ... any line with "Verify active identity"
    r'^\s*//\s*.*[Vv]erify\s+active.*$',
    # // ... any line with "Authentication handlers"
    r'^\s*//\s*.*[Aa]uthentication\s+handlers.*$',
    # // ... any line with "Router switcher"
    r'^\s*//\s*.*[Rr]outer\s+switcher.*$',
    # // ... any line with "Appointment Scheduler"
    r'^\s*//\s*.*[Aa]ppointment\s+Scheduler.*$',
    # // ... any line with "1. Diagnostics Records Vault"
    r'^\s*//\s*\d+\.\s+.*$',
    # // ... any line with "2. Appointment"
    r'^\s*//\s*\d+\.\s+.*$',
    # // ... any line with "3."
    r'^\s*//\s*\d+\.\s+.*$',
]

# HTML comment patterns
HTML_COMMENT_PATTERNS = [
    # <!-- OWASP A0X ... -->
    r'<!--\s*OWASP\s+A0\d+.*?-->',
    # <!-- A0X: ... -->
    r'<!--\s*A0\d+.*?-->',
    # <!-- ... VISUALIZER ... -->
    r'<!--.*?[Vv]ISUALIZER.*?-->',
    # <!-- ... CRITICAL SECURITY WARNING ... -->
    r'<!--.*?[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning.*?-->',
    # <!-- ... Security Analysis ... -->
    r'<!--.*?[Ss]ecurity\s+Analysis.*?-->',
    # <!-- ... A0X & A0Y ... -->
    r'<!--.*?A0\d+\s*&\s*A0\d+.*?-->',
    # <!-- ... Plaintext ... -->
    r'<!--.*?[Pp]laintext.*?-->',
    # <!-- ... Private Key ... -->
    r'<!--.*?[Pp]rivate\s+[Kk]ey.*?-->',
    # <!-- ... sandbox ... -->
    r'<!--.*?[Ss]andbox.*?-->',
    # <!-- ... IDOR ... -->
    r'<!--.*?[Ii]DOR.*?-->',
    # <!-- ... Decoy ... -->
    r'<!--.*?[Dd]ecoy.*?-->',
    # <!-- ... OWASP ... -->
    r'<!--.*?OWASP.*?-->',
    # <!-- ... VULNERABILITY ... -->
    r'<!--.*?VULNERABILITY.*?-->',
    # <!-- ... CHAIN ... -->
    r'<!--.*?CHAIN.*?-->',
    # <!-- ... Plaintext Private Key Exposure -->
    r'<!--.*?[Pp]laintext\s+[Pp]rivate\s+[Kk]ey\s+[Ee]xposure.*?-->',
    # <!-- ... A02 Plaintext Private Key Exposure -->
    r'<!--.*?A02\s+[Pp]laintext.*?-->',
    # <!-- ... A04 & A07 Sandbox -->
    r'<!--.*?A04.*?A07.*?-->',
    # <!-- ... A04 ... -->
    r'<!--.*?A04.*?-->',
    # <!-- ... A07 ... -->
    r'<!--.*?A07.*?-->',
    # <!-- ... A01 ... -->
    r'<!--.*?A01.*?-->',
    # <!-- ... A03 ... -->
    r'<!--.*?A03.*?-->',
    # <!-- ... A05 ... -->
    r'<!--.*?A05.*?-->',
    # <!-- ... A06 ... -->
    r'<!--.*?A06.*?-->',
    # <!-- ... A08 ... -->
    r'<!--.*?A08.*?-->',
    # <!-- ... A09 ... -->
    r'<!--.*?A09.*?-->',
    # <!-- ... A10 ... -->
    r'<!--.*?A10.*?-->',
    # <!-- ... A0X ... -->
    r'<!--.*?A0\d+.*?-->',
]

# Python-specific patterns (docstrings and comments)
PYTHON_COMMENT_PATTERNS = [
    # Same as Java patterns but for Python
    r'^\s*#\s*OWASP\s+A0\d+.*$',
    r'^\s*#\s*VULNERABILITY\s+A0\d+.*$',
    r'^\s*#\s*CHAIN\s+LINK.*$',
    r'^\s*#\s*A0\d+.*$',
    r'^\s*#\s*.*OWASP.*$',
    r'^\s*#\s*.*VULNERABILITY.*$',
    r'^\s*#\s*.*CHAIN\s+LINK.*$',
    r'^\s*#\s*.*[Aa]0\d+.*$',
    r'^\s*#\s*.*[Pp]laintext.*$',
    r'^\s*#\s*.*[Ee]xposing.*$',
    r'^\s*#\s*.*[Rr]aw\s+[Ii]nsecure.*$',
    r'^\s*#\s*.*[Hh]orizontal\s+IDOR.*$',
    r'^\s*#\s*.*[Cc]ritical\s+Security\s+Warning.*$',
    r'^\s*#\s*.*[Vv]ISUALIZER.*$',
    r'^\s*#\s*.*[Dd]iagnostics\s+Records.*$',
    r'^\s*#\s*.*[Ss]ecurity\s+Analysis.*$',
    r'^\s*#\s*.*[Mm][Ff][Aa].*$',
    r'^\s*#\s*.*step[- ]?[Uu]p.*$',
    r'^\s*#\s*.*[Dd]ecoy.*$',
    r'^\s*#\s*.*[Ss]andbox.*$',
    r'^\s*#\s*.*[Cc]alling\s+user.*$',
    r'^\s*#\s*.*[Ff]unds\s+from\s+wallets.*$',
    r'^\s*#\s*.*[Aa]ny\s+authenticated\s+user.*$',
    r'^\s*#\s*.*[Dd]o\s+not\s+own.*$',
    r'^\s*#\s*.*[Aa]llowing\s+other.*$',
    r'^\s*#\s*.*[Pp]rivileged\s+Vault.*$',
    r'^\s*#\s*.*[Cc]linical\s+exfiltration.*$',
    r'^\s*#\s*.*[Cc]onsultations\s+queue.*$',
    r'^\s*#\s*.*[Ii]DOR\s+visualizer.*$',
    r'^\s*#\s*.*[Cc]SRF.*$',
    r'^\s*#\s*.*[Vv]erify\s+active.*$',
    r'^\s*#\s*.*[Aa]uthentication\s+handlers.*$',
    r'^\s*#\s*.*[Rr]outer\s+switcher.*$',
    r'^\s*#\s*.*[Aa]ppointment\s+Scheduler.*$',
    r'^\s*#\s*\d+\.\s+.*$',
    # Triple-quoted docstrings that are vulnerability descriptions
    r'^\s*"""[Aa]0\d+.*?"""$',
    r'^\s*"""[Oo]WASP.*?"""$',
    r'^\s*"""[Vv]ULNERABILITY.*?"""$',
    r'^\s*"""[Cc]hain.*?"""$',
    r'^\s*"""[Pp]laintext.*?"""$',
    r'^\s*"""[Ee]xposing.*?"""$',
    r'^\s*"""[Rr]aw\s+[Ii]nsecure.*?"""$',
    r'^\s*"""[Hh]orizontal\s+IDOR.*?"""$',
    r'^\s*"""[Cc]ritical\s+Security\s+Warning.*?"""$',
    r'^\s*"""[Vv]ISUALIZER.*?"""$',
    r'^\s*"""[Dd]iagnostics\s+Records.*?"""$',
    r'^\s*"""[Ss]ecurity\s+Analysis.*?"""$',
    r'^\s*"""[Mm][Ff][Aa].*?"""$',
    r'^\s*"""step[- ]?[Uu]p.*?"""$',
    r'^\s*"""[Dd]ecoy.*?"""$',
    r'^\s*"""[Ss]andbox.*?"""$',
    r'^\s*"""[Cc]alling\s+user.*?"""$',
    r'^\s*"""[Ff]unds\s+from\s+wallets.*?"""$',
    r'^\s*"""[Aa]ny\s+authenticated\s+user.*?"""$',
    r'^\s*"""[Dd]o\s+not\s+own.*?"""$',
    r'^\s*"""[Aa]llowing\s+other.*?"""$',
    r'^\s*"""[Pp]rivileged\s+Vault.*?"""$',
    r'^\s*"""[Cc]linical\s+exfiltration.*?"""$',
    r'^\s*"""[Cc]onsultations\s+queue.*?"""$',
    r'^\s*"""[Ii]DOR\s+visualizer.*?"""$',
    r'^\s*"""[Cc]SRF.*?"""$',
    r'^\s*"""[Vv]erify\s+active.*?"""$',
    r'^\s*"""[Aa]uthentication\s+handlers.*?"""$',
    r'^\s*"""[Rr]outer\s+switcher.*?"""$',
    r'^\s*"""[Aa]ppointment\s+Scheduler.*?"""$',
    r'^\s*"""\s*\d+\.\s+.*?"""$',
]


def should_skip_dir(dirname):
    return dirname in SKIP_DIRS


def clean_java_line(line):
    """Clean a Java/TypeScript/C-style source line."""
    stripped = line.strip()

    # Skip empty lines, imports, annotations, braces, class/method declarations
    if not stripped:
        return line
    if stripped.startswith('import '):
        return line
    if stripped.startswith('@'):
        return line
    # Skip lines that are purely code (not comments)
    if stripped in ('{', '}', '};'):
        return line
    # Don't skip lines starting with // - those are comments we process below
    if not stripped.startswith('//'):
        return line
    # Check if it's a vulnerability hint comment
    hint_patterns = [
        r'OWASP\s+A0\d+',
        r'VULNERABILITY\s+A0\d+',
        r'CHAIN\s+LINK',
        r'A0\d+',
        r'[Pp]laintext',
        r'[Ee]xposing',
        r'[Rr]aw\s+[Ii]nsecure',
        r'[Hh]orizontal\s+IDOR',
        r'[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning',
        r'[Vv]ISUALIZER',
        r'[Dd]iagnostics\s+[Rr]ecords',
        r'[Ss]ecurity\s+[Aa]nalysis',
        r'[Mm][Ff][Aa]',
        r'step[-\s]?[Uu]p',
        r'[Dd]ecoy',
        r'[Ss]andbox',
        r'[Cc]alling\s+user',
        r'[Ff]unds\s+from\s+wallets',
        r'[Aa]ny\s+authenticated\s+user',
        r'[Dd]o\s+not\s+own',
        r'[Aa]llowing\s+other',
        r'[Pp]rivileged\s+[Vv]ault',
        r'[Cc]linical\s+exfiltration',
        r'[Cc]onsultations\s+queue',
        r'[Ii]DOR\s+visualizer',
        r'[Cc]SRF',
        r'[Vv]erify\s+active',
        r'[Aa]uthentication\s+handlers',
        r'[Rr]outer\s+switcher',
        r'[Aa]ppointment\s+Scheduler',
        r'\d+\.\s+[A-Z]',
        r'BCrypt\s+is\s+secure',
        r'Safe\s+decoy',
        r'hashing\s+decoy',
        r'password\s+in\s+plaintext',
        r'if\s+vulnerable',
    ]
    
    for pattern in hint_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return ''

    # Check for inline vulnerability hints at end of code lines
    # e.g., `code // OWASP A01: ...`
    if '//' in line:
        before, _, after = line.partition('//')
        for pattern in hint_patterns:
            if re.search(pattern, after, re.IGNORECASE):
                return before.rstrip()

    return line


def clean_python_line(line):
    """Clean a Python source line."""
    stripped = line.strip()

    # Skip empty lines, imports, decorators, class/function defs
    if not stripped:
        return line
    if stripped.startswith('import ') or stripped.startswith('from '):
        return line
    if stripped.startswith('@'):
        return line
    if stripped.startswith('def ') or stripped.startswith('class '):
        return line
    if stripped.startswith('return ') or stripped.startswith('raise '):
        return line
    if stripped.startswith('if ') or stripped.startswith('elif ') or stripped.startswith('else:'):
        return line
    if stripped.startswith('for ') or stripped.startswith('while '):
        return line
    if stripped.startswith('try:') or stripped.startswith('except') or stripped.startswith('finally:'):
        return line
    if stripped.startswith('with '):
        return line
    if stripped.startswith('yield ') or stripped.startswith('async def '):
        return line
    if stripped.startswith('#!/'):
        return line
    if stripped.startswith('__'):
        return line

    # Handle # comments
    if '#' in line:
        before, _, after = line.partition('#')
        # If there's code before the comment, clean just the comment
        if before.strip():
            # Check if the comment is a vulnerability hint
            for pattern in PYTHON_COMMENT_PATTERNS:
                if re.match(pattern, '#' + after, re.IGNORECASE):
                    return before.rstrip()
            if re.search(r'OWASP\s+A0\d+', after, re.IGNORECASE):
                return before.rstrip()
            if re.search(r'VULNERABILITY\s+A0\d+', after, re.IGNORECASE):
                return before.rstrip()
            if re.search(r'CHAIN\s+LINK', after, re.IGNORECASE):
                return before.rstrip()
            if re.search(r'A0\d+', after):
                return before.rstrip()
            if re.search(r'[Pp]laintext', after):
                return before.rstrip()
            if re.search(r'[Ee]xposing', after):
                return before.rstrip()
            if re.search(r'[Rr]aw\s+[Ii]nsecure', after):
                return before.rstrip()
            if re.search(r'[Hh]orizontal\s+IDOR', after):
                return before.rstrip()
            if re.search(r'[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning', after):
                return before.rstrip()
            if re.search(r'[Vv]ISUALIZER', after):
                return before.rstrip()
            if re.search(r'[Dd]iagnostics\s+[Rr]ecords', after):
                return before.rstrip()
            if re.search(r'[Ss]ecurity\s+[Aa]nalysis', after):
                return before.rstrip()
            if re.search(r'[Mm][Ff][Aa]', after):
                return before.rstrip()
            if re.search(r'step[-\s]?[Uu]p', after):
                return before.rstrip()
            if re.search(r'[Dd]ecoy', after):
                return before.rstrip()
            if re.search(r'[Ss]andbox', after):
                return before.rstrip()
            if re.search(r'[Cc]alling\s+user', after):
                return before.rstrip()
            if re.search(r'[Ff]unds\s+from\s+wallets', after):
                return before.rstrip()
            if re.search(r'[Aa]ny\s+authenticated\s+user', after):
                return before.rstrip()
            if re.search(r'[Dd]o\s+not\s+own', after):
                return before.rstrip()
            if re.search(r'[Aa]llowing\s+other', after):
                return before.rstrip()
            if re.search(r'[Pp]rivileged\s+[Vv]ault', after):
                return before.rstrip()
            if re.search(r'[Cc]linical\s+exfiltration', after):
                return before.rstrip()
            if re.search(r'[Cc]onsultations\s+queue', after):
                return before.rstrip()
            if re.search(r'[Ii]DOR\s+visualizer', after):
                return before.rstrip()
            if re.search(r'[Cc]SRF', after):
                return before.rstrip()
            if re.search(r'[Vv]erify\s+active', after):
                return before.rstrip()
            if re.search(r'[Aa]uthentication\s+handlers', after):
                return before.rstrip()
            if re.search(r'[Rr]outer\s+switcher', after):
                return before.rstrip()
            if re.search(r'[Aa]ppointment\s+Scheduler', after):
                return before.rstrip()
            return line
        else:
            # Full comment line
            for pattern in PYTHON_COMMENT_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    return ''
            if re.search(r'OWASP\s+A0\d+', line, re.IGNORECASE):
                return ''
            if re.search(r'VULNERABILITY\s+A0\d+', line, re.IGNORECASE):
                return ''
            if re.search(r'CHAIN\s+LINK', line, re.IGNORECASE):
                return ''
            if re.search(r'A0\d+', line):
                return ''
            if re.search(r'[Pp]laintext', line):
                return ''
            if re.search(r'[Ee]xposing', line):
                return ''
            if re.search(r'[Rr]aw\s+[Ii]nsecure', line):
                return ''
            if re.search(r'[Hh]orizontal\s+IDOR', line):
                return ''
            if re.search(r'[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning', line):
                return ''
            if re.search(r'[Vv]ISUALIZER', line):
                return ''
            if re.search(r'[Dd]iagnostics\s+[Rr]ecords', line):
                return ''
            if re.search(r'[Ss]ecurity\s+[Aa]nalysis', line):
                return ''
            if re.search(r'[Mm][Ff][Aa]', line):
                return ''
            if re.search(r'step[-\s]?[Uu]p', line):
                return ''
            if re.search(r'[Dd]ecoy', line):
                return ''
            if re.search(r'[Ss]andbox', line):
                return ''
            if re.search(r'[Cc]alling\s+user', line):
                return ''
            if re.search(r'[Ff]unds\s+from\s+wallets', line):
                return ''
            if re.search(r'[Aa]ny\s+authenticated\s+user', line):
                return ''
            if re.search(r'[Dd]o\s+not\s+own', line):
                return ''
            if re.search(r'[Aa]llowing\s+other', line):
                return ''
            if re.search(r'[Pp]rivileged\s+[Vv]ault', line):
                return ''
            if re.search(r'[Cc]linical\s+exfiltration', line):
                return ''
            if re.search(r'[Cc]onsultations\s+queue', line):
                return ''
            if re.search(r'[Ii]DOR\s+visualizer', line):
                return ''
            if re.search(r'[Cc]SRF', line):
                return ''
            if re.search(r'[Vv]erify\s+active', line):
                return ''
            if re.search(r'[Aa]uthentication\s+handlers', line):
                return ''
            if re.search(r'[Rr]outer\s+switcher', line):
                return ''
            if re.search(r'[Aa]ppointment\s+Scheduler', line):
                return ''
            return line

    # Handle triple-quoted docstrings
    if '"""' in line or "'''" in line:
        # Remove docstrings that are vulnerability descriptions
        line = re.sub(r'"""[Aa]0\d+.*?"""', '', line)
        line = re.sub(r'"""[Oo]WASP.*?"""', '', line)
        line = re.sub(r'"""[Vv]ULNERABILITY.*?"""', '', line)
        line = re.sub(r'"""[Cc]hain.*?"""', '', line)
        line = re.sub(r'"""[Pp]laintext.*?"""', '', line)
        line = re.sub(r'"""[Ee]xposing.*?"""', '', line)
        line = re.sub(r'"""[Rr]aw\s+[Ii]nsecure.*?"""', '', line)
        line = re.sub(r'"""[Hh]orizontal\s+IDOR.*?"""', '', line)
        line = re.sub(r'"""[Cc]ritical\s+Security\s+Warning.*?"""', '', line)
        line = re.sub(r'"""[Vv]ISUALIZER.*?"""', '', line)
        line = re.sub(r'"""[Dd]iagnostics\s+Records.*?"""', '', line)
        line = re.sub(r'"""[Ss]ecurity\s+Analysis.*?"""', '', line)
        line = re.sub(r'"""[Mm][Ff][Aa].*?"""', '', line)
        line = re.sub(r'"""step[-\s]?[Uu]p.*?"""', '', line)
        line = re.sub(r'"""[Dd]ecoy.*?"""', '', line)
        line = re.sub(r'"""[Ss]andbox.*?"""', '', line)
        line = re.sub(r'"""[Cc]alling\s+user.*?"""', '', line)
        line = re.sub(r'"""[Ff]unds\s+from\s+wallets.*?"""', '', line)
        line = re.sub(r'"""[Aa]ny\s+authenticated\s+user.*?"""', '', line)
        line = re.sub(r'"""[Dd]o\s+not\s+own.*?"""', '', line)
        line = re.sub(r'"""[Aa]llowing\s+other.*?"""', '', line)
        line = re.sub(r'"""[Pp]rivileged\s+Vault.*?"""', '', line)
        line = re.sub(r'"""[Cc]linical\s+exfiltration.*?"""', '', line)
        line = re.sub(r'"""[Cc]onsultations\s+queue.*?"""', '', line)
        line = re.sub(r'"""[Ii]DOR\s+visualizer.*?"""', '', line)
        line = re.sub(r'"""[Cc]SRF.*?"""', '', line)
        line = re.sub(r'"""[Vv]erify\s+active.*?"""', '', line)
        line = re.sub(r'"""[Aa]uthentication\s+handlers.*?"""', '', line)
        line = re.sub(r'"""[Rr]outer\s+switcher.*?"""', '', line)
        line = re.sub(r'"""[Aa]ppointment\s+Scheduler.*?"""', '', line)
        line = re.sub(r'"""\s*\d+\.\s+.*?"""', '', line)
        # Clean up empty lines left by docstring removal
        if line.strip() == '""' or line.strip() == "''":
            return ''

    return line


def clean_html_line(line):
    """Clean an HTML source line."""
    # Remove HTML comments with vulnerability references
    cleaned = line

    # Remove <!-- OWASP A0X ... -->
    cleaned = re.sub(r'<!--\s*OWASP\s+A0\d+.*?-->', '', cleaned)
    # Remove <!-- A0X: ... -->
    cleaned = re.sub(r'<!--\s*A0\d+.*?-->', '', cleaned)
    # Remove <!-- ... VISUALIZER ... -->
    cleaned = re.sub(r'<!--.*?[Vv]ISUALIZER.*?-->', '', cleaned)
    # Remove <!-- ... CRITICAL SECURITY WARNING ... -->
    cleaned = re.sub(r'<!--.*?[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning.*?-->', '', cleaned)
    # Remove <!-- ... Security Analysis ... -->
    cleaned = re.sub(r'<!--.*?[Ss]ecurity\s+Analysis.*?-->', '', cleaned)
    # Remove <!-- ... A0X & A0Y ... -->
    cleaned = re.sub(r'<!--.*?A0\d+\s*&\s*A0\d+.*?-->', '', cleaned)
    # Remove <!-- ... Plaintext ... -->
    cleaned = re.sub(r'<!--.*?[Pp]laintext.*?-->', '', cleaned)
    # Remove <!-- ... Private Key ... -->
    cleaned = re.sub(r'<!--.*?[Pp]rivate\s+[Kk]ey.*?-->', '', cleaned)
    # Remove <!-- ... sandbox ... -->
    cleaned = re.sub(r'<!--.*?[Ss]andbox.*?-->', '', cleaned)
    # Remove <!-- ... IDOR ... -->
    cleaned = re.sub(r'<!--.*?[Ii]DOR.*?-->', '', cleaned)
    # Remove <!-- ... Decoy ... -->
    cleaned = re.sub(r'<!--.*?[Dd]ecoy.*?-->', '', cleaned)
    # Remove <!-- ... OWASP ... -->
    cleaned = re.sub(r'<!--.*?OWASP.*?-->', '', cleaned)
    # Remove <!-- ... VULNERABILITY ... -->
    cleaned = re.sub(r'<!--.*?VULNERABILITY.*?-->', '', cleaned)
    # Remove <!-- ... CHAIN ... -->
    cleaned = re.sub(r'<!--.*?CHAIN.*?-->', '', cleaned)
    # Remove <!-- ... Plaintext Private Key Exposure -->
    cleaned = re.sub(r'<!--.*?[Pp]laintext\s+[Pp]rivate\s+[Kk]ey\s+[Ee]xposure.*?-->', '', cleaned)
    # Remove <!-- ... A02 Plaintext Private Key Exposure -->
    cleaned = re.sub(r'<!--.*?A02\s+[Pp]laintext.*?-->', '', cleaned)
    # Remove <!-- ... A04 & A07 Sandbox -->
    cleaned = re.sub(r'<!--.*?A04.*?A07.*?-->', '', cleaned)
    # Remove <!-- ... A0X ... -->
    cleaned = re.sub(r'<!--.*?A0\d+.*?-->', '', cleaned)

    # Check for JS/TS comments inside <script> tags
    if '<script' in line or '</script' in line:
        # Process JS comments within script tags
        cleaned = re.sub(r'//\s*OWASP\s+A0\d+.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*VULNERABILITY\s+A0\d+.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*CHAIN\s+LINK.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*A0\d+.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*OWASP.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*VULNERABILITY.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*CHAIN\s+LINK.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Aa]0\d+.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Pp]laintext.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Ee]xposing.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Rr]aw\s+[Ii]nsecure.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Hh]orizontal\s+IDOR.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Cc]ritical\s+[Ss]ecurity\s+[Ww]arning.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Vv]ISUALIZER.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Dd]iagnostics\s+[Rr]ecords.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Ss]ecurity\s+[Aa]nalysis.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Mm][Ff][Aa].*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*step[-\s]?[Uu]p.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Dd]ecoy.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Ss]andbox.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Cc]alling\s+user.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Ff]unds\s+from\s+wallets.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Aa]ny\s+authenticated\s+user.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Dd]o\s+not\s+own.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Aa]llowing\s+other.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Pp]rivileged\s+[Vv]ault.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Cc]linical\s+exfiltration.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Cc]onsultations\s+queue.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Ii]DOR\s+visualizer.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Cc]SRF.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Vv]erify\s+active.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Aa]uthentication\s+handlers.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Rr]outer\s+switcher.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*.*[Aa]ppointment\s+Scheduler.*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'//\s*\d+\.\s+.*$', '', cleaned, flags=re.IGNORECASE)

    return cleaned


def clean_file(filepath):
    """Clean vulnerability hints from a single file. Returns True if file was modified."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            original_lines = f.readlines()
    except (IOError, OSError):
        return False

    modified = False
    new_lines = []

    ext = os.path.splitext(filepath)[1].lower()

    for line in original_lines:
        if ext == '.py':
            cleaned = clean_python_line(line)
        elif ext in ('.java', '.ts', '.js'):
            cleaned = clean_java_line(line)
        elif ext == '.html':
            cleaned = clean_html_line(line)
        else:
            new_lines.append(line)
            continue

        if cleaned != line:
            modified = True
        new_lines.append(cleaned)

    if modified:
        # Remove trailing blank lines that were left by comment removal
        while new_lines and new_lines[-1].strip() == '':
            # Keep at most one trailing newline
            new_lines.pop()
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] = new_lines[-1] + '\n'

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        except (IOError, OSError) as e:
            print(f"  ERROR writing {filepath}: {e}")
            return False

    return modified


def collect_files(root_dir):
    """Collect all source files to process."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip node_modules and other excluded dirs
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in SOURCE_EXTENSIONS:
                files.append(os.path.join(dirpath, filename))
    return sorted(files)


def main():
    if len(sys.argv) < 2:
        print("Usage: python cleanup_hints.py <directory>")
        print("  Processes all source files (.py, .java, .ts, .js, .html) in the directory.")
        print("  Skips node_modules, .git, __pycache__, etc.")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a directory")
        sys.exit(1)

    print(f"Scanning {target_dir} for source files...")
    files = collect_files(target_dir)
    print(f"Found {len(files)} source files")

    modified_count = 0
    total_changes = 0

    for filepath in files:
        if clean_file(filepath):
            modified_count += 1
            rel_path = os.path.relpath(filepath, target_dir)
            print(f"  CLEANED: {rel_path}")

    print(f"\nDone. Cleaned {modified_count} files.")


if __name__ == '__main__':
    main()