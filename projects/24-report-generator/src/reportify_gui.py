"""
Reportify Pro - Enterprise Report Generator GUI
==============================================

A professional tkinter-based GUI for generating enterprise reports
with 25+ templates across 7 IT domains.

Features:
- Three-panel modern UI (Categories | Templates | Form Editor)
- Smart variables and auto-population
- Tag system with suggestions
- Risk and timeline management
- Multi-format export (DOCX)

Usage:
    python reportify_gui.py

Dependencies:
    pip install python-docx pillow

Author: Portfolio Showcase
Version: 2.1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
from datetime import datetime
from pathlib import Path
import sys

# Import from reportify_pro module
try:
    from reportify_pro import (
        ReportData, REPORT_TEMPLATES, ReportCategory,
        DocumentGenerator, ProjectFileManager,
        Risk, TimelineEntry, TechnicalSpec
    )
except ImportError:
    print("Error: reportify_pro module required. Ensure reportify_pro.py is in the same directory.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

TAG_SUGGESTIONS = [
    "critical", "high-priority", "security", "compliance", "infrastructure",
    "cloud", "devops", "audit", "assessment", "optimization", "vulnerability",
    "penetration-test", "incident-response", "migration", "cost-analysis",
    "performance", "monitoring", "automation", "network", "database"
]

RISK_CATEGORIES = [
    "Technical", "Security", "Operational", "Financial", "Legal",
    "Compliance", "Resource", "Schedule", "Scope", "Quality",
    "Performance", "Availability", "Data Loss", "Integration"
]

RISK_IMPACTS = ["Critical", "High", "Medium", "Low", "Negligible"]
RISK_LIKELIHOODS = ["Certain", "Likely", "Possible", "Unlikely", "Rare"]
TIMELINE_STATUSES = ["Not Started", "Planned", "In Progress", "On Hold", "Completed", "Delayed", "At Risk"]


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════

class ListManager(ttk.Frame):
    """Widget for managing lists of items"""
    def __init__(self, parent, title):
        super().__init__(parent)

        ttk.Label(self, text=title, font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x', pady=5)

        self.entry = ttk.Entry(input_frame)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry.bind('<Return>', lambda e: self._add_item())

        ttk.Button(input_frame, text="Add", command=self._add_item, width=8).pack(side='left')

        self.listbox = tk.Listbox(self, height=6)
        self.listbox.pack(fill='both', expand=True, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Remove", command=self._remove_item, width=10).pack(side='left', padx=2)

    def _add_item(self):
        value = self.entry.get().strip()
        if value:
            self.listbox.insert(tk.END, value)
            self.entry.delete(0, tk.END)

    def _remove_item(self):
        selection = self.listbox.curselection()
        if selection:
            self.listbox.delete(selection[0])

    def get_items(self):
        return list(self.listbox.get(0, tk.END))

    def set_items(self, items):
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, item)


class TagEntry(ttk.Frame):
    """Widget for managing tags with suggestions"""
    def __init__(self, parent, suggestions):
        super().__init__(parent)
        self.suggestions = suggestions
        self.tags = []

        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x', pady=5)

        self.entry = ttk.Combobox(input_frame, values=suggestions)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry.bind('<Return>', lambda e: self._add_tag())

        ttk.Button(input_frame, text="Add Tag", command=self._add_tag, width=10).pack(side='left')

        self.tag_frame = ttk.Frame(self)
        self.tag_frame.pack(fill='x')

    def _add_tag(self):
        tag = self.entry.get().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self._render_tags()
            self.entry.delete(0, tk.END)

    def _remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self._render_tags()

    def _render_tags(self):
        for widget in self.tag_frame.winfo_children():
            widget.destroy()

        for tag in self.tags:
            tag_widget = ttk.Frame(self.tag_frame, relief='raised', borderwidth=1)
            tag_widget.pack(side='left', padx=2, pady=2)

            ttk.Label(tag_widget, text=tag).pack(side='left', padx=5)
            ttk.Button(tag_widget, text="×", width=2, command=lambda t=tag: self._remove_tag(t)).pack(side='left')

    def get_tags(self):
        return self.tags.copy()

    def set_tags(self, tags):
        self.tags = tags.copy()
        self._render_tags()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class ReportifyProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reportify Pro v2.1 - Enterprise Report Generator")
        self.root.geometry("1400x900")

        self.data = ReportData()
        self.current_file = None
        self.current_template = None

        self._create_ui()
        self._show_category(ReportCategory.SECURITY)

    def _create_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Report", command=self._new_report)
        file_menu.add_command(label="Open...", command=self._open_project)
        file_menu.add_command(label="Save", command=self._save_project)
        file_menu.add_command(label="Save As...", command=self._save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export as DOCX", command=self._export_docx)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)

        # Left sidebar - Categories
        sidebar = ttk.Frame(main_container, width=180)
        sidebar.pack(side='left', fill='y', padx=5, pady=5)
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="Reportify\nPro", font=('Arial', 18, 'bold')).pack(pady=20)
        ttk.Label(sidebar, text="v2.1", font=('Arial', 10)).pack()
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)

        self.category_buttons = {}
        for category in ReportCategory:
            display_name = category.value.replace('_', ' ').title()
            btn = ttk.Button(
                sidebar,
                text=display_name,
                command=lambda c=category: self._show_category(c),
                width=18
            )
            btn.pack(pady=5, padx=5, fill='x')
            self.category_buttons[category] = btn

        # Middle panel - Template gallery
        self.template_panel = ttk.Frame(main_container, width=320)
        self.template_panel.pack(side='left', fill='y', pady=5)
        self.template_panel.pack_propagate(False)

        template_header = ttk.Frame(self.template_panel)
        template_header.pack(fill='x', padx=10, pady=10)

        self.template_title = ttk.Label(template_header, text="Templates", font=('Arial', 12, 'bold'))
        self.template_title.pack(anchor='w')

        ttk.Separator(self.template_panel, orient='horizontal').pack(fill='x', padx=10)

        canvas = tk.Canvas(self.template_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.template_panel, orient='vertical', command=canvas.yview)
        self.template_list_frame = ttk.Frame(canvas)

        self.template_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.template_list_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True, padx=5)
        scrollbar.pack(side='right', fill='y')

        # Right panel - Content editor
        content_area = ttk.Frame(main_container)
        content_area.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Top bar with actions
        top_bar = ttk.Frame(content_area)
        top_bar.pack(fill='x', pady=(0, 10))

        self.report_title_label = ttk.Label(top_bar, text="New Report", font=('Arial', 14, 'bold'))
        self.report_title_label.pack(side='left')

        action_frame = ttk.Frame(top_bar)
        action_frame.pack(side='right')

        ttk.Button(action_frame, text="💾 Save", command=self._save_project, width=10).pack(side='left', padx=2)
        ttk.Button(action_frame, text="📄 Export", command=self._export_docx, width=10).pack(side='left', padx=2)

        ttk.Separator(content_area, orient='horizontal').pack(fill='x', pady=5)

        # Scrollable form area
        form_canvas = tk.Canvas(content_area, highlightthickness=0)
        form_scrollbar = ttk.Scrollbar(content_area, orient='vertical', command=form_canvas.yview)
        self.form_frame = ttk.Frame(form_canvas)

        self.form_frame.bind(
            "<Configure>",
            lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all"))
        )

        form_canvas.create_window((0, 0), window=self.form_frame, anchor='nw')
        form_canvas.configure(yscrollcommand=form_scrollbar.set)

        form_canvas.pack(side='left', fill='both', expand=True)
        form_scrollbar.pack(side='right', fill='y')

        # Status bar
        status_bar = ttk.Frame(content_area)
        status_bar.pack(fill='x', pady=(5, 0))

        self.status_label = ttk.Label(status_bar, text="Ready", relief='sunken')
        self.status_label.pack(fill='x')

        self._create_form()

    def _show_category(self, category):
        # Clear template list
        for widget in self.template_list_frame.winfo_children():
            widget.destroy()

        display_name = category.value.replace('_', ' ').title()
        self.template_title.config(text=f"{display_name} Reports")

        # Display templates for category
        for key, template in REPORT_TEMPLATES.items():
            if template['category'] == category:
                card = self._create_template_card(key, template)
                card.pack(fill='x', padx=5, pady=5)

    def _create_template_card(self, key, template):
        card = ttk.LabelFrame(self.template_list_frame, text="", padding=10)

        # Icon and name
        header = ttk.Frame(card)
        header.pack(fill='x')

        ttk.Label(header, text=template['icon'], font=('Arial', 16)).pack(side='left', padx=(0, 10))

        text_frame = ttk.Frame(header)
        text_frame.pack(side='left', fill='x', expand=True)

        ttk.Label(text_frame, text=template['name'], font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(text_frame, text=template['description'], font=('Arial', 8), wraplength=220).pack(anchor='w')

        # Use button
        ttk.Button(card, text="Use Template", command=lambda: self._load_template(key)).pack(fill='x', pady=(10, 0))

        return card

    def _load_template(self, template_key):
        template = REPORT_TEMPLATES[template_key]
        self.current_template = template

        self.data = ReportData(
            template_key=template_key,
            category=template['category'].value
        )

        # Apply defaults
        defaults = template.get('defaults', {})
        self.data.title = defaults.get('title', template['name'])
        self.data.objectives = defaults.get('objectives', []).copy()
        if 'methodology' in defaults:
            self.data.methodology = defaults['methodology']

        self.report_title_label.config(text=template['name'])
        self._populate_form()
        self.status_label.config(text=f"Loaded template: {template['name']}")

    def _create_form(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.form_frame)
        notebook.pack(fill='both', expand=True)

        # Tab 1: Basic Info
        basic_tab = ttk.Frame(notebook, padding=10)
        notebook.add(basic_tab, text="Basic Info")

        # Title
        ttk.Label(basic_tab, text="Report Title *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.title_entry = ttk.Entry(basic_tab, width=60, font=('Arial', 11))
        self.title_entry.pack(fill='x', pady=(0, 15))

        # Subtitle
        ttk.Label(basic_tab, text="Subtitle", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.subtitle_entry = ttk.Entry(basic_tab, width=60)
        self.subtitle_entry.pack(fill='x', pady=(0, 15))

        # Company and Author in columns
        info_frame = ttk.Frame(basic_tab)
        info_frame.pack(fill='x', pady=(0, 15))

        left_col = ttk.Frame(info_frame)
        left_col.pack(side='left', fill='x', expand=True, padx=(0, 10))

        ttk.Label(left_col, text="Company Name", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.company_entry = ttk.Entry(left_col)
        self.company_entry.insert(0, "Your Company Inc.")
        self.company_entry.pack(fill='x')

        right_col = ttk.Frame(info_frame)
        right_col.pack(side='left', fill='x', expand=True)

        ttk.Label(right_col, text="Author", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.author_entry = ttk.Entry(right_col)
        self.author_entry.pack(fill='x')

        # Executive Summary
        ttk.Label(basic_tab, text="Executive Summary", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.summary_text = scrolledtext.ScrolledText(basic_tab, height=6, wrap=tk.WORD)
        self.summary_text.pack(fill='x', pady=(0, 15))

        # Tab 2: Content
        content_tab = ttk.Frame(notebook, padding=10)
        notebook.add(content_tab, text="Content")

        # Objectives
        self.objectives_manager = ListManager(content_tab, "Objectives")
        self.objectives_manager.pack(fill='x', pady=(0, 15))

        # Scope
        ttk.Label(content_tab, text="Scope", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.scope_text = scrolledtext.ScrolledText(content_tab, height=4, wrap=tk.WORD)
        self.scope_text.pack(fill='x', pady=(0, 15))

        # Methodology
        ttk.Label(content_tab, text="Methodology", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.methodology_text = scrolledtext.ScrolledText(content_tab, height=4, wrap=tk.WORD)
        self.methodology_text.pack(fill='x', pady=(0, 15))

        # Findings
        self.findings_manager = ListManager(content_tab, "Key Findings")
        self.findings_manager.pack(fill='x', pady=(0, 15))

        # Recommendations
        self.recommendations_manager = ListManager(content_tab, "Recommendations")
        self.recommendations_manager.pack(fill='x', pady=(0, 15))

        # Tab 3: Analysis & Conclusion
        analysis_tab = ttk.Frame(notebook, padding=10)
        notebook.add(analysis_tab, text="Analysis")

        # Analysis
        ttk.Label(analysis_tab, text="Analysis", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.analysis_text = scrolledtext.ScrolledText(analysis_tab, height=6, wrap=tk.WORD)
        self.analysis_text.pack(fill='x', pady=(0, 15))

        # Conclusion
        ttk.Label(analysis_tab, text="Conclusion", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.conclusion_text = scrolledtext.ScrolledText(analysis_tab, height=6, wrap=tk.WORD)
        self.conclusion_text.pack(fill='x', pady=(0, 15))

        # Next Steps
        self.next_steps_manager = ListManager(analysis_tab, "Next Steps")
        self.next_steps_manager.pack(fill='x', pady=(0, 15))

        # Tab 4: Metadata
        metadata_tab = ttk.Frame(notebook, padding=10)
        notebook.add(metadata_tab, text="Metadata")

        # Tags
        ttk.Label(metadata_tab, text="Tags", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.tag_entry = TagEntry(metadata_tab, TAG_SUGGESTIONS)
        self.tag_entry.pack(fill='x', pady=(0, 15))

        # Status and Classification
        status_frame = ttk.Frame(metadata_tab)
        status_frame.pack(fill='x', pady=(0, 15))

        left_col = ttk.Frame(status_frame)
        left_col.pack(side='left', fill='x', expand=True, padx=(0, 10))

        ttk.Label(left_col, text="Status", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.status_combo = ttk.Combobox(left_col, values=["Draft", "In Review", "Approved", "Final"])
        self.status_combo.set("Draft")
        self.status_combo.pack(fill='x')

        right_col = ttk.Frame(status_frame)
        right_col.pack(side='left', fill='x', expand=True)

        ttk.Label(right_col, text="Classification", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.classification_combo = ttk.Combobox(right_col, values=["Public", "Internal", "Confidential", "Restricted"])
        self.classification_combo.set("Internal")
        self.classification_combo.pack(fill='x')

    def _populate_form(self):
        """Populate form with current data"""
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, self.data.title)

        self.subtitle_entry.delete(0, tk.END)
        self.subtitle_entry.insert(0, self.data.subtitle)

        self.company_entry.delete(0, tk.END)
        self.company_entry.insert(0, self.data.company_name)

        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, self.data.author)

        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', self.data.executive_summary)

        self.objectives_manager.set_items(self.data.objectives)

        self.scope_text.delete('1.0', tk.END)
        self.scope_text.insert('1.0', self.data.scope)

        self.methodology_text.delete('1.0', tk.END)
        self.methodology_text.insert('1.0', self.data.methodology)

        self.findings_manager.set_items(self.data.findings)
        self.recommendations_manager.set_items(self.data.recommendations)

        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', self.data.analysis)

        self.conclusion_text.delete('1.0', tk.END)
        self.conclusion_text.insert('1.0', self.data.conclusion)

        self.next_steps_manager.set_items(self.data.next_steps)

        self.tag_entry.set_tags(self.data.tags)
        self.status_combo.set(self.data.status)
        self.classification_combo.set(self.data.classification)

    def _collect_data(self):
        """Collect data from form"""
        self.data.title = self.title_entry.get()
        self.data.subtitle = self.subtitle_entry.get()
        self.data.company_name = self.company_entry.get()
        self.data.author = self.author_entry.get()
        self.data.executive_summary = self.summary_text.get('1.0', tk.END).strip()
        self.data.objectives = self.objectives_manager.get_items()
        self.data.scope = self.scope_text.get('1.0', tk.END).strip()
        self.data.methodology = self.methodology_text.get('1.0', tk.END).strip()
        self.data.findings = self.findings_manager.get_items()
        self.data.recommendations = self.recommendations_manager.get_items()
        self.data.analysis = self.analysis_text.get('1.0', tk.END).strip()
        self.data.conclusion = self.conclusion_text.get('1.0', tk.END).strip()
        self.data.next_steps = self.next_steps_manager.get_items()
        self.data.tags = self.tag_entry.get_tags()
        self.data.status = self.status_combo.get()
        self.data.classification = self.classification_combo.get()
        return self.data

    def _new_report(self):
        if messagebox.askyesno("New Report", "Create new report? Unsaved changes will be lost."):
            self.data = ReportData()
            self.current_file = None
            self.current_template = None
            self._populate_form()
            self.status_label.config(text="New report created")

    def _save_project(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_project_as()

    def _save_project_as(self):
        self._collect_data()

        filename = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            self._save_to_file(Path(filename))

    def _save_to_file(self, file_path):
        try:
            ProjectFileManager.save_project(self.data, file_path)
            self.current_file = file_path
            self.status_label.config(text=f"Saved: {file_path.name}")
            messagebox.showinfo("Success", "Project saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _open_project(self):
        filename = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.data = ProjectFileManager.load_project(Path(filename))
                if self.data:
                    self._populate_form()
                    self.current_file = Path(filename)

                    # Load template if available
                    if self.data.template_key in REPORT_TEMPLATES:
                        self.current_template = REPORT_TEMPLATES[self.data.template_key]
                        self.report_title_label.config(text=self.current_template['name'])

                    self.status_label.config(text=f"Opened: {Path(filename).name}")
                else:
                    messagebox.showerror("Error", "Failed to load project")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open: {e}")

    def _export_docx(self):
        if not self.data.title:
            messagebox.showwarning("Warning", "Please enter a report title")
            return

        self._collect_data()

        # Use current template or default
        template = self.current_template or REPORT_TEMPLATES['vulnerability_assessment']

        filename = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".docx",
            initialfile=f"{self.data.title}.docx",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
        )

        if filename:
            try:
                DocumentGenerator.generate_report(self.data, template, Path(filename))
                self.status_label.config(text=f"Exported: {Path(filename).name}")
                messagebox.showinfo("Success", f"Report exported successfully!\n\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def _show_about(self):
        about_text = """
Reportify Pro v2.1.0
Enterprise Report Generator

Features:
• 25+ Professional Templates
• 7+ IT Domain Categories
• Smart Variables & Automation
• Risk & Timeline Management
• Multi-Format Export

Created for Portfolio Showcase
        """
        messagebox.showinfo("About Reportify Pro", about_text)


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    app = ReportifyProApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
