#!/usr/bin/env python3
"""
create_documents.py - Generate end-of-year meeting documents from markdown files.

This script reads markdown files from the content/ directory and generates:
- script_mentee.pdf (with fillable form fields)
- script_mentor.pdf (with fillable form fields)
- skill_assessment.pdf (with rating squares and target circles)

Output files are saved to the outputs/ directory.
"""

import os
import sys
from pathlib import Path
import endoy


def main():
    """
    Main function to generate all meeting documents.

    Reads from content/ directory:
    - script.md -> outputs/script_mentee.pdf (Mentee role with form fields)
    - script.md -> outputs/script_mentor.pdf (Mentor role with form fields)
    - skills.md -> outputs/skill_assessment.pdf
    """
    # Define paths
    content_dir = Path('content')
    output_dir = Path('outputs')

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Generating end-of-year meeting documents...")
    print("=" * 60)

    # ========================================================================
    # Parse script.md (used for both mentee and mentor PDFs)
    # ========================================================================
    script_md = content_dir / 'script.md'
    if not script_md.exists():
        print(f"  ERROR: {script_md} not found")
        sys.exit(1)

    script_data = endoy.parse_markdown_file(str(script_md))

    # ========================================================================
    # Generate script_mentee.pdf
    # ========================================================================
    try:
        print("\n[1/3] Generating script_mentee.pdf...")

        mentee_latex = endoy.generate_latex_script(script_data, role='Mentee')

        # Save LaTeX to temporary file
        tex_output = output_dir / 'script_mentee.tex'
        endoy.save_latex_file(mentee_latex, str(tex_output))

        # Compile to PDF
        mentee_output = output_dir / 'script_mentee.pdf'
        print(f"  → Compiling LaTeX to PDF...")

        success = endoy.compile_latex_to_pdf(str(tex_output), str(mentee_output))

        if success:
            print(f"  ✓ Generated: {mentee_output}")
            tex_output.unlink()
        else:
            print(f"  ERROR: Failed to compile PDF")
            print(f"  LaTeX source saved at: {tex_output}")
            sys.exit(1)

    except Exception as e:
        print(f"  ERROR generating script_mentee.pdf: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # Generate script_mentor.pdf
    # ========================================================================
    try:
        print("\n[2/3] Generating script_mentor.pdf...")

        mentor_latex = endoy.generate_latex_script(script_data, role='Mentor')

        # Save LaTeX to temporary file
        tex_output = output_dir / 'script_mentor.tex'
        endoy.save_latex_file(mentor_latex, str(tex_output))

        # Compile to PDF
        mentor_output = output_dir / 'script_mentor.pdf'
        print(f"  → Compiling LaTeX to PDF...")

        success = endoy.compile_latex_to_pdf(str(tex_output), str(mentor_output))

        if success:
            print(f"  ✓ Generated: {mentor_output}")
            tex_output.unlink()
        else:
            print(f"  ERROR: Failed to compile PDF")
            print(f"  LaTeX source saved at: {tex_output}")
            sys.exit(1)

    except Exception as e:
        print(f"  ERROR generating script_mentor.pdf: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # Generate skill_assessment.pdf (via LaTeX)
    # ========================================================================
    try:
        print("\n[3/3] Generating skill_assessment.pdf...")
        skills_md = content_dir / 'skills.md'

        if not skills_md.exists():
            print(f"  ERROR: {skills_md} not found")
            sys.exit(1)

        skills_data = endoy.parse_markdown_file(str(skills_md))
        skills_latex = endoy.generate_latex_skills(skills_data)

        # Save LaTeX to temporary file
        tex_output = output_dir / 'skill_assessment.tex'
        endoy.save_latex_file(skills_latex, str(tex_output))
        print(f"  ✓ Generated LaTeX: {tex_output}")

        # Compile to PDF
        pdf_output = output_dir / 'skill_assessment.pdf'
        print(f"  → Compiling LaTeX to PDF...")

        success = endoy.compile_latex_to_pdf(str(tex_output), str(pdf_output))

        if success:
            print(f"  ✓ Generated: {pdf_output}")
            # Clean up .tex file
            #tex_output.unlink()
        else:
            print(f"  ERROR: Failed to compile PDF")
            print(f"  LaTeX source saved at: {tex_output}")
            sys.exit(1)

    except Exception as e:
        print(f"  ERROR generating skill_assessment.pdf: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 60)
    print("✓ All documents generated successfully!")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  - {output_dir / 'script_mentee.pdf'}")
    print(f"  - {output_dir / 'script_mentor.pdf'}")
    print(f"  - {output_dir / 'skill_assessment.pdf'}")
    print()


if __name__ == '__main__':
    main()