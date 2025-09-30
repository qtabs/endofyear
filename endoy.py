"""
endoy.py - Library for generating end-of-year meeting materials.

This library reads markdown content files and generates PDF documents
with fillable form fields for academic mentor/mentee end-of-year meetings.
"""

import re
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any


# ============================================================================
# Markdown Parsing Functions
# ============================================================================

def parse_markdown(markdown_content: str) -> Dict[str, Any]:
    """
    Parse markdown content and extract title, sections, subsections, and bullet points.

    Args:
        markdown_content: String containing markdown text

    Returns:
        Dictionary with structure:
        {
            'title': str,
            'sections': [
                {
                    'header': str,
                    'subsections': [
                        {
                            'header': str,  # 'Mentee', 'Mentor', 'Both', or 'Both*'
                            'items': [str, ...]
                        },
                        ...
                    ]
                },
                ...
            ]
        }
    """
    lines = markdown_content.strip().split('\n')
    result = {
        'title': '',
        'sections': []
    }

    current_section = None
    current_subsection = None

    for line in lines:
        line = line.rstrip()

        # Match H1 header (# Title)
        if line.startswith('# '):
            result['title'] = line[2:].strip()

        # Match H2 header (## Section)
        elif line.startswith('## '):
            # Save previous subsection to previous section if exists
            if current_subsection is not None and current_section is not None:
                current_section['subsections'].append(current_subsection)

            # Save previous section if exists
            if current_section is not None:
                result['sections'].append(current_section)

            # Start new section
            current_section = {
                'header': line[3:].strip(),
                'subsections': [],
                'items': []  # Support direct items under section
            }
            current_subsection = None

        # Match H3 header (### Mentee/Mentor/Both/Both*)
        elif line.startswith('### '):
            if current_section is not None:
                # Save previous subsection if exists
                if current_subsection is not None:
                    current_section['subsections'].append(current_subsection)

                # Start new subsection
                current_subsection = {
                    'header': line[4:].strip(),
                    'items': []
                }

        # Match bullet point (- Item)
        elif line.startswith('- '):
            item_text = line[2:].strip()
            if current_subsection is not None:
                # Add to current subsection
                current_subsection['items'].append(item_text)
            elif current_section is not None:
                # Add directly to current section (for simple structures like skills.md)
                current_section['items'].append(item_text)

    # Add last subsection and section if they exist
    if current_subsection is not None and current_section is not None:
        current_section['subsections'].append(current_subsection)
    if current_section is not None:
        result['sections'].append(current_section)

    return result


def parse_markdown_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a markdown file from disk.

    Args:
        file_path: Path to markdown file

    Returns:
        Parsed markdown structure (see parse_markdown)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return parse_markdown(content)


# ============================================================================
# RTF Generation Functions
# ============================================================================

def escape_rtf(text: str) -> str:
    """
    Escape special characters for RTF format.

    Args:
        text: Plain text string

    Returns:
        RTF-escaped string
    """
    # RTF special characters that need escaping
    replacements = {
        '\\': '\\\\',
        '{': '\\{',
        '}': '\\}',
    }

    result = text
    for char, escaped in replacements.items():
        result = result.replace(char, escaped)

    return result


def generate_latex_script(parsed_data: Dict[str, Any], role: str = 'Mentee') -> str:
    """
    Generate LaTeX document for script with fillable form fields based on role.

    Args:
        parsed_data: Output from parse_markdown()
        role: 'Mentee' or 'Mentor' - determines which questions get form fields

    Returns:
        LaTeX document as string
    """
    latex_lines = [
        r'\documentclass[9pt,a4paper]{article}',
        r'\usepackage[margin=1in]{geometry}',
        r'\usepackage{hyperref}',
        r'\usepackage{xcolor}',
        r'\usepackage{needspace}',
        r'',
        r'% Configure form field appearance',
        r'\hypersetup{',
        r'    pdfborder={0 0 0}',
        r'}',
        r'',
        r'\begin{document}',
        r'',
    ]

    # Add title with role
    if parsed_data['title']:
        title = escape_latex(parsed_data['title'])
        latex_lines.append(r'\begin{center}')
        latex_lines.append(r'{\Large\bfseries ' + title + r' (' + role + r')}')
        latex_lines.append(r'\end{center}')
        latex_lines.append(r'')
        latex_lines.append(r'\vspace{0.5cm}')
        latex_lines.append(r'')

    # Add instructions
    latex_lines.append(r'\noindent\textbf{Instructions:}')
    latex_lines.append(r'')
    latex_lines.append(r'\vspace{0.2cm}')
    latex_lines.append(r'')
    latex_lines.append(r'\noindent This script is designed to help you prepare for and guide your end-of-year meeting. Questions in black are meant for you to answer and have fillable text fields. Questions in gray (prefixed with ``' + ('Mentor' if role == 'Mentee' else 'Mentee') + r':'') are for the other person and are provided for your reference. Items in italics are instructions or actions to be completed.')
    latex_lines.append(r'')
    latex_lines.append(r'\vspace{0.2cm}')
    latex_lines.append(r'')
    latex_lines.append(r'\noindent\textbf{Preparation:} Please complete this form \textit{before} the meeting. Thoughtful preparation is essential---take time to reflect deeply on each question. Your honest, considered responses will make the meeting more productive and meaningful for both parties.')
    latex_lines.append(r'')
    latex_lines.append(r'\vspace{0.5cm}')
    latex_lines.append(r'')

    field_counter = 1

    # Add sections
    for section in parsed_data['sections']:
        # Section header (H2) - keep with content
        header = escape_latex(section['header'])
        latex_lines.append(r'\needspace{6cm}')
        latex_lines.append(r'\noindent\textbf{\large ' + header + r'}')
        latex_lines.append(r'')
        latex_lines.append(r'\vspace{0.3cm}')
        latex_lines.append(r'')

        # Process subsections (H3: Mentee/Mentor/Both/Both*/Mentee*/Mentor*)
        for subsection in section['subsections']:
            subsection_header = subsection['header']

            # Check if header ends with * (action/instruction)
            header_is_action = subsection_header.endswith('*')
            header_base = subsection_header.rstrip('*')

            # Determine subsection type
            is_both = header_base == 'Both'
            is_my_role = header_base == role
            is_other_role = header_base in ['Mentee', 'Mentor'] and not is_my_role and not is_both

            # For headers ending with * (actions/instructions for everyone in that category)
            if header_is_action:
                for item in subsection['items']:
                    item_text = escape_latex(item.rstrip('*').strip())
                    latex_lines.append(r'\noindent\textit{' + item_text + r'}')
                    latex_lines.append(r'')
                    latex_lines.append(r'\vspace{0.3cm}')
                    latex_lines.append(r'')

            # For "Both" (questions for both to answer separately)
            elif is_both:
                for item in subsection['items']:
                    # Check if item ends with * (action, no field)
                    item_is_action = item.endswith('*')
                    item_text = escape_latex(item.rstrip('*').strip())

                    if item_is_action:
                        # Action item - show in italics, no fields
                        latex_lines.append(r'\noindent\textit{' + item_text + r'}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.3cm}')
                        latex_lines.append(r'')
                    else:
                        # Question - mentee's field first
                        field_name = f'field{field_counter}'
                        field_counter += 1

                        latex_lines.append(r'\needspace{4cm}')
                        latex_lines.append(r'\noindent ' + item_text)
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.3em}')
                        latex_lines.append(r'\noindent\TextField[name=' + field_name + r',multiline=true,width=\textwidth,height=2.5cm,bordercolor={0 0 0},backgroundcolor={0.95 0.95 0.95}]{}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.2cm}')
                        latex_lines.append(r'')

                        # Then mentor's field with gray label
                        other_role = 'Mentor' if role == 'Mentee' else 'Mentee'
                        field_name = f'field{field_counter}'
                        field_counter += 1

                        latex_lines.append(r'\needspace{4cm}')
                        latex_lines.append(r'\noindent{\color{gray}' + other_role + r': ' + item_text + r'}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.3em}')
                        latex_lines.append(r'\noindent\TextField[name=' + field_name + r',multiline=true,width=\textwidth,height=2.5cm,bordercolor={0 0 0},backgroundcolor={0.95 0.95 0.95}]{}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.4cm}')
                        latex_lines.append(r'')

            # For my role's questions: show in black with form fields
            elif is_my_role:
                for item in subsection['items']:
                    # Check if item ends with * (action, no field)
                    item_is_action = item.endswith('*')
                    item_text = escape_latex(item.rstrip('*').strip())

                    if item_is_action:
                        # Action item - show in italics, no field
                        latex_lines.append(r'\noindent\textit{' + item_text + r'}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.3cm}')
                        latex_lines.append(r'')
                    else:
                        # Question - show with field
                        field_name = f'field{field_counter}'
                        field_counter += 1

                        # Keep question and field together
                        latex_lines.append(r'\needspace{4cm}')
                        latex_lines.append(r'\noindent ' + item_text)
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.3em}')
                        # Multi-line text field
                        latex_lines.append(r'\noindent\TextField[name=' + field_name + r',multiline=true,width=\textwidth,height=2.5cm,bordercolor={0 0 0},backgroundcolor={0.95 0.95 0.95}]{}')
                        latex_lines.append(r'')
                        latex_lines.append(r'\vspace{0.4cm}')
                        latex_lines.append(r'')

            # For other role's questions: show in gray without form fields
            elif is_other_role:
                # Determine the other role's name for the label
                other_role = 'Mentor' if role == 'Mentee' else 'Mentee'
                for item in subsection['items']:
                    item_text = escape_latex(item.rstrip('*').strip())
                    latex_lines.append(r'\noindent{\color{gray}' + other_role + r': ' + item_text + r'}')
                    latex_lines.append(r'')
                    latex_lines.append(r'\vspace{0.15cm}')
                    latex_lines.append(r'')

        latex_lines.append(r'\vspace{0.3cm}')
        latex_lines.append(r'')

    latex_lines.append(r'\end{document}')

    return '\n'.join(latex_lines)


def save_rtf_file(rtf_content: str, file_path: str) -> None:
    """
    Save RTF content to file.

    Args:
        rtf_content: RTF document string
        file_path: Output file path
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rtf_content)


# ============================================================================
# LaTeX Generation Functions
# ============================================================================

def escape_latex(text: str) -> str:
    """
    Escape special characters for LaTeX.

    Args:
        text: Plain text string

    Returns:
        LaTeX-escaped string
    """
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }

    result = text
    for char, escaped in replacements.items():
        result = result.replace(char, escaped)

    return result


def generate_latex_skills(parsed_data: Dict[str, Any]) -> str:
    """
    Generate LaTeX document for skills assessment with rating squares and target circle.

    Args:
        parsed_data: Output from parse_markdown()

    Returns:
        LaTeX document as string
    """
    latex_lines = [
        r'\documentclass[9pt,a4paper]{article}',
        r'\usepackage[margin=1in]{geometry}',
        r'\usepackage{array}',
        r'\usepackage{amssymb}',
        r'\usepackage{pifont}',
        r'\usepackage{tikz}',
        r'\usepackage{hyperref}',
        r'\pagestyle{empty}',
        r'',
        r'% Define rating and checkbox commands as clickable form fields',
        r'% Rating squares: each gets unique name for independent clicking',
        r'\newcommand{\ratingcircle}[2]{%',
        r'  \raisebox{-0ex}{\CheckBox[name=#1_#2,width=1.2ex,height=1.2ex,bordercolor={0 0 0},borderstyle=S,borderwidth=1]{}}%',
        r'}',
        r'% Target checkbox - static empty circle (no clicking behavior needed)',
        r'\newcommand{\checkbox}[1]{\raisebox{-0.6ex}{\tikz\draw[very thick] (0,0) circle (1.2ex);}}',
        r'',
        r'\begin{document}',
        r'',
        r'\begin{center}',
        r'{\Large\bfseries Assessment of skills for next year planning}',
        r'\end{center}',
        r'',
        r'\vspace{0.2cm}',
        r'',
        r'% Header with labels - 4-column: text | circles block (centered) | spacer | checkbox (right to margin)',
        r'\noindent',
        r'\begin{tabular}{@{}p{\dimexpr\textwidth-3cm-2em-1cm\relax}',
        r'                >{\centering\arraybackslash}p{2.4cm}',
        r'                p{2em}',
        r'                >{\centering\arraybackslash}p{1cm}@{}}',
        r'	& {\small current ability } & & \\',
        r'	& \begin{tabular*}{2.4cm}{@{}l@{\extracolsep{\fill}}r@{}}',
        r'    \small poor & \small great',
        r'  \end{tabular*} & & {\small target} \\',
        r'\end{tabular}',
        r'',
        r'',
        r'',
        r'\vspace{0.3cm}',
        r'',
    ]

    # Add sections
    skill_counter = 1
    for section in parsed_data['sections']:
        # Section header (bold)
        header = escape_latex(section['header'])
        latex_lines.append(r'\noindent\textbf{' + header + r'}\\[0.1cm]')

        # Get items - handle both old structure (direct items) and new structure (subsections)
        items = []
        if 'items' in section:
            # Old structure: section has direct items
            items = section['items']
        elif 'subsections' in section:
            # New structure: section has subsections with items
            for subsection in section['subsections']:
                items.extend(subsection.get('items', []))

        # Section items with rating squares and target circle
        for item in items:
            item_text = escape_latex(item)
            skill_name = f'skill{skill_counter}'
            skill_counter += 1

            # Create row with 4 columns: text | squares | spacer | circle
            latex_lines.append(
                r'\noindent\begin{tabular}{@{}p{\dimexpr\textwidth-3cm-2em-1cm\relax}'
            )
            latex_lines.append(
                r'                >{\arraybackslash}p{2.4cm}'
            )
            latex_lines.append(
                r'                p{2em}'
            )
            latex_lines.append(
                r'                >{\centering\arraybackslash}p{1cm}@{}}'
            )
            latex_lines.append(
                r'		' + item_text + r' &'
            )
            latex_lines.append(
                r'\begin{tabular*}{2.4cm}{@{}c@{\extracolsep{\fill}}c@{\extracolsep{\fill}}c@{\extracolsep{\fill}}c@{\extracolsep{\fill}}c@{}}'
            )
            latex_lines.append(
                r'\ratingcircle{' + skill_name + r'}{1} & \ratingcircle{' + skill_name + r'}{2} & \ratingcircle{' + skill_name + r'}{3} & \ratingcircle{' + skill_name + r'}{4} & \ratingcircle{' + skill_name + r'}{5}'
            )
            latex_lines.append(
                r'\end{tabular*} & & \checkbox{' + skill_name + r'target}'
            )
            latex_lines.append(r'\end{tabular}\\[0.08cm]')

        latex_lines.append(r'')

    latex_lines.append(r'\end{document}')

    return '\n'.join(latex_lines)


def save_latex_file(latex_content: str, file_path: str) -> None:
    """
    Save LaTeX content to file.

    Args:
        latex_content: LaTeX document string
        file_path: Output file path
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)


# ============================================================================
# PDF Compilation Functions
# ============================================================================

def compile_latex_to_pdf(tex_path: str, output_pdf_path: str) -> bool:
    """
    Compile LaTeX file to PDF using pdflatex.

    Args:
        tex_path: Path to .tex file
        output_pdf_path: Desired path for output PDF

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get directory of tex file
        tex_dir = os.path.dirname(os.path.abspath(tex_path))
        tex_file = os.path.basename(tex_path)

        # Run pdflatex twice (for proper formatting)
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                cwd=tex_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

        # Check if PDF was actually generated (more reliable than return code)
        generated_pdf = os.path.join(tex_dir, tex_file.replace('.tex', '.pdf'))

        if not os.path.exists(generated_pdf):
            print(f"pdflatex failed to generate PDF")
            if result.returncode != 0:
                print(f"pdflatex error: {result.stderr}")
            return False

        # Move/copy PDF to desired location if different

        if generated_pdf != output_pdf_path:
            import shutil
            shutil.move(generated_pdf, output_pdf_path)

        # Clean up auxiliary files
        base_name = tex_file.replace('.tex', '')
        aux_extensions = ['.aux', '.log', '.out']
        for ext in aux_extensions:
            aux_file = os.path.join(tex_dir, base_name + ext)
            if os.path.exists(aux_file):
                os.remove(aux_file)

        return True

    except subprocess.TimeoutExpired:
        print("pdflatex compilation timed out")
        return False
    except FileNotFoundError:
        print("pdflatex not found. Please install TeX Live or similar LaTeX distribution.")
        return False
    except Exception as e:
        print(f"Error during PDF compilation: {e}")
        return False