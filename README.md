# endoy

**End-of-Year Meeting Document Generator for Academic Mentorship**

A Python library that generates professional, interactive PDF documents for structured end-of-year meetings between mentors and mentees in academic settings.

## Overview

`endoy` helps academic mentors and mentees conduct meaningful, well-documented annual review meetings. It transforms simple markdown files into polished PDF documents with fillable form fields, ensuring both parties come prepared with thoughtful reflections on the past year and plans for the future.

## Features

- **Role-Specific Meeting Scripts**: Generates separate PDFs for mentors and mentees, each highlighting their own questions while showing the other person's questions for context
- **Skills Assessment Forms**: Interactive skill evaluation sheets with clickable rating scales and target-setting checkboxes
- **Fillable PDF Forms**: All response fields are fillable, allowing participants to prepare digitally or print and complete by hand
- **Markdown-Driven**: Define your meeting structure once in markdown, generate documents automatically
- **Professional Formatting**: Clean 9pt layout with proper spacing, page break protection, and visual distinction between roles
- **Included Templates**: Ships with default meeting script and skills assessment content ready to use or customize

## Generated Documents

Running `endoy` produces three PDF files:

1. **`script_mentee.pdf`** - Mentee's version with fillable fields for their questions, mentor's questions shown in gray
2. **`script_mentor.pdf`** - Mentor's version with fillable fields for their questions, mentee's questions shown in gray
3. **`skill_assessment.pdf`** - Joint skills evaluation form with rating scales and target checkboxes

## Requirements

- **Python**: 3.7 or higher
- **LaTeX Distribution**: TeX Live, MacTeX, or similar (must include `pdflatex`)
  - On macOS: `brew install --cask mactex`
  - On Ubuntu/Debian: `sudo apt-get install texlive-latex-extra`
  - On Windows: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/endoy.git
   cd endoy
   ```

2. Verify LaTeX is installed:
   ```bash
   pdflatex --version
   ```

## Usage

### Quick Start

Generate all documents with default content:

```bash
python3 create_documents.py
```

This will create three PDFs in the `outputs/` directory.

### Using as a Library

```python
import endoy

# Parse markdown content
script_data = endoy.parse_markdown_file('content/script.md')
skills_data = endoy.parse_markdown_file('content/skills.md')

# Generate role-specific scripts
mentee_latex = endoy.generate_latex_script(script_data, role='Mentee')
mentor_latex = endoy.generate_latex_script(script_data, role='Mentor')

# Generate skills assessment
skills_latex = endoy.generate_latex_skills(skills_data)

# Save and compile to PDF
endoy.save_latex_file(mentee_latex, 'script_mentee.tex')
endoy.compile_latex_to_pdf('script_mentee.tex', 'script_mentee.pdf')
```

## Content Structure

### Meeting Script (`content/script.md`)

The script file uses a hierarchical markdown structure:

```markdown
# End-of-Year meeting script

## Section Name

### Mentee
- Question for the mentee?
- Another question for the mentee?
- Action item for the mentee to do*

### Mentor
- Question for the mentor?
- Another question for the mentor?

### Both
- Question for both to answer separately?
- Another question for both?

### Both*
- Joint action or instruction for both to do together*

### Mentee*
- Action item for the mentee (no field needed)*
```

**Header Meanings:**
- `# Title` - Document title (H1)
- `## Section` - Major topic area (H2)
- `### Mentee` - Questions for the mentee to answer with form fields (H3)
- `### Mentor` - Questions for the mentor to answer with form fields (H3)
- `### Both` - Questions for both to answer; mentee's field appears first, then mentor's field with gray label
- `### Both*` - Joint instructions/actions for both (shown in italics, no form fields)
- `### Mentee*` or `### Mentor*` - Actions for that role (shown in italics, no form fields)

**Item-Level Asterisk:**
- Items ending with `*` are treated as actions/instructions rather than questions and do not get form fields

### Skills Assessment (`content/skills.md`)

```markdown
# Individual Development Plan - Skills List

## Skill Category Name
- Specific skill or competency
- Another skill in this category
- Yet another skill

## Another Category
- More skills here
```

Each bullet point becomes a row with:
- 5 clickable rating squares (poor → great)
- 1 target circle for marking development goals

## Customization

### Modifying Questions

Edit `content/script.md` to customize meeting questions. The structure is flexible—add or remove sections as needed.

### Modifying Skills

Edit `content/skills.md` to define relevant skills for your field or institution.

### Styling Changes

Key formatting options in `endoy.py`:

- **Font size**: Line 161 - `\documentclass[9pt,a4paper]{article}`
- **Margins**: Line 162 - `\usepackage[margin=1in]{geometry}`
- **Form field height**: Line 239 - `height=2.5cm`
- **Form field background**: Line 239 - `backgroundcolor={0.95 0.95 0.95}`

## Project Structure

```
endoy/
├── endoy.py                  # Main library
├── create_documents.py       # Document generation script
├── content/
│   ├── script.md            # Meeting script content (included template)
│   └── skills.md            # Skills assessment content (included template)
└── outputs/
    ├── script_mentee.pdf    # Generated mentee document
    ├── script_mentor.pdf    # Generated mentor document
    └── skill_assessment.pdf # Generated skills form
```

The repository includes ready-to-use templates in the `content/` directory:
- **`script.md`**: Comprehensive meeting script with questions covering tasks, responsibilities, reflection, collaboration, workload, planning, and feedback
- **`skills.md`**: Skills assessment framework with categories for scientific knowledge, research skills, communication, project management, teaching, outreach, and career development

These templates can be used as-is or customized to fit your specific needs and institutional context.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional output formats (HTML, Word)
- Internationalization/translation support
- Template library for different academic fields
- Web-based form builder
- Response compilation/analysis tools

## License

[Add your chosen license here]

## Acknowledgments

This tool was inspired by best practices in academic mentorship and individual development planning (IDP) frameworks used at the TU-Dresden.

