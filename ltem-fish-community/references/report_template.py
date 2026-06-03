"""
LTEM Technical Report Generator
=================================

Generates publication-quality technical reports in Markdown, HTML, and PDF
formats, following the CBMC Cabo Pulmo monitoring report structure.

Usage
-----
    from report_template import LTEMReportGenerator

    report = LTEMReportGenerator(
        title="Fish Community Analysis",
        region="Cabo Pulmo",
        period="Spring-Fall 2025"
    )
    report.add_section(...)
    report.export_all(output_dir="my_report/", base_name="ltem_report")

Output
------
    my_report/ltem_report.md    ← Markdown source
    my_report/ltem_report.html  ← Self-contained HTML (figures embedded)
    my_report/ltem_report.pdf   ← PDF (requires: pip install weasyprint)

Dependencies
------------
    Required : pandas, markdown (pip install markdown)
    Optional : weasyprint (pip install weasyprint)  ← needed for PDF only
"""

import os
import re
import base64
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# ── Optional dependencies ────────────────────────────────────────────────────
try:
    import markdown as _md_lib
    _MARKDOWN_AVAILABLE = True
except ImportError:
    _MARKDOWN_AVAILABLE = False

try:
    from weasyprint import HTML as _WeasyprintHTML
    _WEASYPRINT_AVAILABLE = True
except ImportError:
    _WEASYPRINT_AVAILABLE = False

# ── CSS for HTML / PDF output ─────────────────────────────────────────────────
_CSS = """
<style>
  :root {
    --ocean-dark:   #023E8A;
    --ocean-mid:    #0077B6;
    --ocean-light:  #90E0EF;
    --accent:       #00B4D8;
    --bg:           #F8FBFF;
    --surface:      #FFFFFF;
    --text:         #1a1a2e;
    --muted:        #64748b;
    --border:       #c8dff0;
  }

  /* ── Reset & base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { font-size: 15px; }
  body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.75;
    color: var(--text);
    background: var(--bg);
    max-width: 960px;
    margin: 0 auto;
    padding: 48px 36px 96px;
  }

  /* ── Typography ── */
  h1 {
    font-size: 1.85em;
    color: var(--ocean-dark);
    border-bottom: 3px solid var(--ocean-mid);
    padding-bottom: 10px;
    margin: 48px 0 16px;
  }
  h2 {
    font-size: 1.4em;
    color: var(--ocean-dark);
    border-bottom: 1px solid var(--ocean-light);
    padding-bottom: 6px;
    margin: 40px 0 12px;
  }
  h3 { font-size: 1.15em; color: var(--ocean-mid); margin: 28px 0 10px; }
  h4 { font-size: 1em; color: #445; margin: 20px 0 8px; }
  p  { margin: 10px 0; }
  a  { color: var(--ocean-mid); }
  strong { color: var(--ocean-dark); }
  em     { color: var(--muted); }

  /* ── Lists ── */
  ul, ol { margin: 10px 0 10px 28px; }
  li     { margin: 5px 0; }

  /* ── Code ── */
  code {
    background: #e8f4f8;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.87em;
    color: #1a4a6e;
  }
  pre {
    background: #e8f4f8;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 18px 0;
    border-left: 4px solid var(--ocean-mid);
  }
  pre code { padding: 0; background: none; }

  /* ── Tables ── */
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 0.91em;
    background: var(--surface);
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-radius: 6px;
    overflow: hidden;
  }
  thead { background: var(--ocean-dark); color: #fff; }
  th { padding: 10px 15px; text-align: left; font-weight: 600; }
  td { padding: 8px 15px; border-bottom: 1px solid var(--border); }
  tr:last-child td { border-bottom: none; }
  tbody tr:nth-child(even) td { background: #eaf5fb; }
  tbody tr:hover td { background: #d4ecf7; }

  /* ── Figures ── */
  figure {
    margin: 28px 0;
    text-align: center;
  }
  img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
    border-radius: 6px;
    box-shadow: 0 2px 14px rgba(0, 0, 0, 0.13);
  }
  figcaption, .fig-caption {
    margin-top: 10px;
    font-size: 0.88em;
    color: var(--muted);
    line-height: 1.5;
    text-align: left;
    max-width: 860px;
    margin-left: auto;
    margin-right: auto;
  }

  /* ── Dividers ── */
  hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 40px 0;
  }

  /* ── Blockquote ── */
  blockquote {
    border-left: 4px solid var(--ocean-light);
    padding: 10px 20px;
    color: var(--muted);
    margin: 18px 0;
    background: #f0f8ff;
    border-radius: 0 4px 4px 0;
  }

  /* ── Cover page ── */
  .cover {
    text-align: center;
    padding: 48px 0 32px;
    border-bottom: 2px solid var(--ocean-mid);
    margin-bottom: 40px;
  }
  .cover h1 {
    font-size: 1.6em;
    border: none;
    margin: 0 0 8px;
    line-height: 1.3;
  }
  .cover .period  { font-size: 1.15em; color: var(--ocean-mid); margin: 8px 0; }
  .cover .meta    { font-size: 0.9em;  color: var(--muted); margin: 4px 0; }
  .cover .inst    { font-size: 0.88em; color: var(--muted); margin-top: 20px; font-style: italic; }

  /* ── TOC ── */
  .toc {
    background: #eaf5fb;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 28px;
    margin: 32px 0;
    font-size: 0.93em;
  }
  .toc h2 { border: none; margin-top: 0; font-size: 1.05em; color: var(--ocean-dark); }
  .toc ul { margin: 0; list-style: none; padding: 0; }
  .toc li { margin: 4px 0; }
  .toc a  { color: var(--ocean-mid); text-decoration: none; }
  .toc a:hover { text-decoration: underline; }

  /* ── Footer ── */
  footer {
    margin-top: 72px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    font-size: 0.82em;
    color: var(--muted);
    text-align: center;
  }

  /* ── Print / PDF overrides ── */
  @media print {
    body     { max-width: none; padding: 20mm 25mm; font-size: 11pt; }
    h1       { page-break-before: always; font-size: 16pt; }
    h1:first-of-type { page-break-before: avoid; }
    h2       { font-size: 13pt; }
    img      { max-width: 100%; page-break-inside: avoid; }
    table    { page-break-inside: avoid; font-size: 9pt; }
    .toc     { page-break-after: always; }
    .no-print { display: none; }
  }
</style>
"""


class LTEMReportGenerator:
    """
    Generate comprehensive LTEM technical reports (Markdown, HTML, PDF).

    Report structure
    ----------------
    1. Cover / Title
    2. Table of Contents
    3. Introduction
    4. Results & Discussion  (one or more sections)
    5. Conclusion
    6. Monitoring Protocol
    7. References
    """

    def __init__(
        self,
        title: str,
        region: str,
        period: str,
        authors: Optional[List[Dict]] = None,
        institution: str = "Centro para la Biodiversidad Marina y la Conservación, A.C.",
        language: str = "es",
    ):
        self.title       = title
        self.region      = region
        self.period      = period
        self.authors     = authors or []
        self.institution = institution
        self.language    = language
        self.sections    = []
        self.figures     = []
        self.tables      = []
        self.references  = []
        self.generated_date = datetime.now()
        self.labels = self._get_labels(language)

    # ── Language labels ──────────────────────────────────────────────────────
    def _get_labels(self, lang: str) -> Dict[str, str]:
        labels = {
            "es": {
                "toc": "Contenido",
                "introduction": "Introducción",
                "results": "Resultados y Discusión",
                "conclusion": "Conclusión",
                "protocol": "Protocolo de monitoreo",
                "references": "Referencias",
                "figures": "Figuras",
                "figure": "Figura",
                "table": "Tabla",
                "generated": "Generado",
                "by": "Realizado por",
                "participants": "Participantes de expedición",
                "methods": "Métodos",
                "data_summary": "Resumen de Datos",
            },
            "en": {
                "toc": "Contents",
                "introduction": "Introduction",
                "results": "Results & Discussion",
                "conclusion": "Conclusion",
                "protocol": "Monitoring Protocol",
                "references": "References",
                "figures": "Figures",
                "figure": "Figure",
                "table": "Table",
                "generated": "Generated",
                "by": "Prepared by",
                "participants": "Expedition participants",
                "methods": "Methods",
                "data_summary": "Data Summary",
            },
        }
        return labels.get(lang, labels["en"])

    # ── Content builders ─────────────────────────────────────────────────────
    def add_author(self, name: str, degree: str, affiliation: str, role: str = "author"):
        self.authors.append({"name": name, "degree": degree,
                              "affiliation": affiliation, "role": role})

    def add_section(self, title: str, content: str,
                    section_type: str = "results",
                    subsections: Optional[List[Dict]] = None):
        self.sections.append({"title": title, "content": content,
                               "type": section_type, "subsections": subsections or []})

    def add_figure(self, path: str, caption: str, number: Optional[int] = None) -> str:
        if number is None:
            number = len(self.figures) + 1
        self.figures.append({"number": number, "path": path, "caption": caption})
        return (f"![{self.labels['figure']} {number}]({path})\n\n"
                f"**{self.labels['figure']} {number}.** {caption}")

    def add_table(self, df: pd.DataFrame, caption: str,
                  number: Optional[int] = None) -> str:
        if number is None:
            number = len(self.tables) + 1
        self.tables.append({"number": number, "data": df, "caption": caption})
        return (f"**{self.labels['table']} {number}.** {caption}\n\n"
                f"{df.to_markdown(index=False)}")

    def add_reference(self, citation: str):
        if citation not in self.references:
            self.references.append(citation)

    # ── Markdown section builders ─────────────────────────────────────────────
    def _generate_cover(self) -> str:
        # chatMPA Studio identity logo
        logo_path = "../positron-product-icons/chatMPA_identity_logo.png"

        cover = (f"# INFORME TÉCNICO DE MONITOREO ECOLÓGICO:\n"
                 f"# {self.region.upper()}\n\n"
                 f"## {self.period}\n\n---\n\n"
                 f'<p align="center">\n'
                 f'  <img src="{logo_path}" width="200" alt="chatMPA Studio">\n'
                 f'</p>\n\n'
                 f"**{self.labels['generated']}:** "
                 f"{self.generated_date.strftime('%Y-%m-%d')}\n\n")
        if self.authors:
            cover += f"**{self.labels['by']}:**\n\n"
            for a in self.authors:
                if a["role"] == "author":
                    cover += f"- {a['degree']} {a['name']} ({a['affiliation']})\n"
            participants = [a for a in self.authors if a["role"] == "participant"]
            if participants:
                cover += f"\n**{self.labels['participants']}:**\n\n"
                for p in participants:
                    cover += f"- {p['degree']} {p['name']} ({p['affiliation']})\n"
        cover += f"\n---\n\n*{self.institution}*\n"
        cover += f"*Powered by chatMPA Studio*\n\n"
        return cover

    def _generate_toc(self) -> str:
        toc = f"## {self.labels['toc']}\n\n"
        toc += f"1. [{self.labels['introduction']}](#introducción)\n"
        toc += f"2. [{self.labels['results']}](#resultados-y-discusión)\n"
        for i, s in enumerate([s for s in self.sections if s["type"] == "results"], 1):
            anchor = (s["title"].lower()
                      .replace(" ", "-")
                      .translate(str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")))
            toc += f"   {i}. [{s['title']}](#{anchor})\n"
        toc += f"3. [{self.labels['conclusion']}](#conclusión)\n"
        toc += f"4. [{self.labels['protocol']}](#protocolo-de-monitoreo)\n"
        toc += f"5. [{self.labels['references']}](#referencias)\n\n"
        return toc

    def _generate_introduction(self) -> str:
        intro = f"## {self.labels['introduction']}\n\n"
        intro_sections = [s for s in self.sections if s["type"] == "introduction"]
        if intro_sections:
            for s in intro_sections:
                intro += s["content"] + "\n\n"
        else:
            intro += self._default_introduction()
        return intro

    def _default_introduction(self) -> str:
        if "cabo pulmo" in self.region.lower():
            return """El Parque Nacional Cabo Pulmo (PNCP) es una de las áreas naturales protegidas más
emblemáticas del Golfo de California. Ubicado en la costa oriental de Baja California Sur,
el parque fue decretado como Área Natural Protegida en 1995 y recategorizado a Parque
Nacional en el año 2000. La recuperación ecológica del parque ha sido extraordinaria: entre
1999 y 2009, la biomasa total de peces aumentó más del 460%, convirtiéndose en uno de los
casos de recuperación marina más documentados del mundo (Aburto-Oropeza et al. 2011).

"""
        return (f"Este informe presenta los resultados del monitoreo ecológico realizado en la región "
                f"de {self.region} durante el periodo {self.period}. El Programa de Monitoreo Ecológico a "
                f"Largo Plazo (LTEM) del Golfo de California proporciona datos sistemáticos sobre las "
                f"comunidades de peces e invertebrados en los arrecifes rocosos de la región desde 1998.\n\n")

    def _generate_results(self) -> str:
        out = f"## {self.labels['results']}\n\n"
        for s in [s for s in self.sections if s["type"] == "results"]:
            out += f"### {s['title']}\n\n{s['content']}\n\n"
            for sub in s.get("subsections", []):
                out += f"#### {sub['title']}\n\n{sub['content']}\n\n"
        return out

    def _generate_figures(self) -> str:
        """Generate a Figures section with all added figures."""
        if not self.figures:
            return ""
        out = f"## {self.labels.get('figures', 'Figuras')}\n\n"
        for fig in self.figures:
            out += f"![{self.labels['figure']} {fig['number']}]({fig['path']})\n\n"
            out += f"**{self.labels['figure']} {fig['number']}.** {fig['caption']}\n\n"
        return out

    def _generate_conclusion(self) -> str:
        out = f"## {self.labels['conclusion']}\n\n"
        for s in [s for s in self.sections if s["type"] == "conclusion"]:
            out += s["content"] + "\n\n"
        return out

    def _generate_protocol(self) -> str:
        out = f"## {self.labels['protocol']}\n\n"
        protocol_sections = [s for s in self.sections if s["type"] == "protocol"]
        if protocol_sections:
            for s in protocol_sections:
                out += s["content"] + "\n\n"
        else:
            out += self._default_protocol()
        return out

    def _default_protocol(self) -> str:
        return """El LTEM obtiene sus datos mediante transectos visuales estandarizados aplicados
sistemáticamente desde 1998 en los arrecifes rocosos del Golfo de California.

### Diseño de muestreo

- **Transectos**: 4 por sitio (2 a 5 m y 2 a 20 m de profundidad)
- **Área por transecto**: 250 m² para peces (50 m × 5 m)
- **Réplicas**: 4 transectos por estrato de profundidad

### Variables registradas

| Variable | Método | Unidades |
|----------|--------|----------|
| Abundancia | Conteo visual | ind/transecto |
| Talla | Estimación visual | cm (intervalos de 5 cm) |
| Biomasa | Calculada (W = aL^b) | ton/ha |
| Especies | Identificación in situ | Presencia/abundancia |

### Cálculo de biomasa

```
W = a × TL^b
Biomasa = Σ(W × N) / Área
```
"""

    def _generate_references(self) -> str:
        out = f"## {self.labels['references']}\n\n"
        if self.references:
            for ref in sorted(self.references):
                out += f"- {ref}\n\n"
        else:
            out += self._default_references()
        return out

    def _default_references(self) -> str:
        return (
            "Aburto-Oropeza, O., et al. (2011). Large recovery of fish biomass in a no-take "
            "marine reserve. *PLoS ONE*, 6(8), e23601.\n\n"
            "Favoretto, F., et al. (2024). Trophic restructuring and warming-driven "
            "tropicalization in Gulf of California rocky reefs. *Global Change Biology*.\n\n"
            "Frölicher, T. L., et al. (2018). Marine heatwaves under global warming. "
            "*Nature*, 560(7718), 360–364.\n\n"
        )

    def _generate_footer(self) -> str:
        """Generate chatMPA Studio branded footer with logo."""
        logo_path = "../positron-product-icons/chatMPA_identity_logo.png"
        timestamp = self.generated_date.strftime('%Y-%m-%d %H:%M')

        footer = f"""---

## About chatMPA Studio

chatMPA Studio is an open-source marine science IDE that combines:
- Python & R data analysis with integrated consoles
- Jupyter Notebooks for reproducible research
- Data Explorer for visualizing marine datasets
- AI-powered coding assistance
- Pre-built marine science workflows

**Learn more:** https://github.com/Fabbiologia/chatmpa-studio

---

<p align="center">
  <img src="{logo_path}" width="150" alt="chatMPA Studio">
</p>

<p align="center">
  <strong>Built with chatMPA Studio for Marine Conservation</strong><br>
  <em>Generated with chatMPA Studio – {timestamp}</em>
</p>
"""
        return footer

    # ── Core Markdown generator ───────────────────────────────────────────────
    def _build_markdown(self) -> str:
        """Assemble the complete Markdown report."""
        parts = [
            self._generate_cover(), "---\n\n",
            self._generate_toc(),   "---\n\n",
            self._generate_introduction(), "---\n\n",
            self._generate_results(), "---\n\n",
        ]
        # Add figures section if any figures were added
        if self.figures:
            parts.extend([self._generate_figures(), "---\n\n"])
        parts.extend([
            self._generate_conclusion(), "---\n\n",
            self._generate_protocol(), "---\n\n",
            self._generate_references(),
            self._generate_footer(),
        ])
        return "".join(parts)

    # ── HTML conversion helpers ───────────────────────────────────────────────
    @staticmethod
    def _embed_images(html: str, base_dir: str) -> str:
        """Replace relative img src paths with inline base64 data URIs."""
        def replacer(m):
            src = m.group(1)
            if src.startswith("data:") or src.startswith("http"):
                return m.group(0)
            img_path = os.path.normpath(os.path.join(base_dir, src))
            if not os.path.exists(img_path):
                return m.group(0)
            ext  = os.path.splitext(img_path)[1].lower().lstrip(".")
            mime = {"png": "image/png", "jpg": "image/jpeg",
                    "jpeg": "image/jpeg", "gif": "image/gif",
                    "svg": "image/svg+xml"}.get(ext, "image/png")
            with open(img_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f'src="data:{mime};base64,{data}"'
        return re.sub(r'src="([^"]+)"', replacer, html)

    @staticmethod
    def _md_to_body(md_text: str) -> str:
        """Convert Markdown to HTML body using the markdown package."""
        if not _MARKDOWN_AVAILABLE:
            raise ImportError(
                "The 'markdown' package is required for HTML export.\n"
                "Install with: pip install markdown"
            )
        import markdown as _md
        extensions = ["tables", "fenced_code", "toc", "nl2br", "attr_list"]
        return _md.markdown(md_text, extensions=extensions)

    # ── Public export methods ─────────────────────────────────────────────────
    def generate(self, output_path: Optional[str] = None) -> str:
        """
        Generate Markdown report (backward-compatible).

        Parameters
        ----------
        output_path : str, optional
            If given, saves the Markdown to this path.

        Returns
        -------
        str
            Complete report as a Markdown string.
        """
        md = self._build_markdown()
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Markdown report saved: {output_path}")
        return md

    def to_html(
        self,
        output_path: Optional[str] = None,
        embed_images: bool = True,
        figures_dir: Optional[str] = None,
    ) -> str:
        """
        Generate a self-contained HTML report.

        Parameters
        ----------
        output_path : str, optional
            If given, saves the HTML file to this path.
        embed_images : bool
            If True, converts all local images to inline base64 (default: True).
        figures_dir : str, optional
            Base directory for resolving relative image paths.
            Defaults to the directory of output_path (or cwd).

        Returns
        -------
        str
            Complete HTML document as a string.
        """
        md_text   = self._build_markdown()
        body_html = self._md_to_body(md_text)

        if embed_images:
            base_dir = figures_dir or (
                os.path.dirname(os.path.abspath(output_path))
                if output_path else os.getcwd()
            )
            body_html = self._embed_images(body_html, base_dir)

        html_doc = (
            f'<!DOCTYPE html>\n<html lang="{self.language}">\n<head>\n'
            f'  <meta charset="UTF-8">\n'
            f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'  <title>{self.title} – {self.region}</title>\n'
            f'  {_CSS}\n'
            f'</head>\n<body>\n'
            f'{body_html}\n'
            f'</body>\n</html>'
        )

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_doc)
            print(f"HTML report saved:     {output_path}")
        return html_doc

    def to_pdf(
        self,
        output_path: str,
        figures_dir: Optional[str] = None,
    ) -> bool:
        """
        Generate a PDF report via weasyprint.

        Parameters
        ----------
        output_path : str
            Destination .pdf file path.
        figures_dir : str, optional
            Base directory for resolving relative image paths.

        Returns
        -------
        bool
            True if PDF was saved successfully, False otherwise.

        Notes
        -----
        Requires: pip install weasyprint
        macOS:    brew install pango libffi  (if weasyprint install fails)
        """
        if not _WEASYPRINT_AVAILABLE:
            print(
                "⚠  PDF export requires weasyprint.\n"
                "   Install: pip install weasyprint\n"
                "   macOS:   brew install pango libffi  (if needed)\n"
                f"   Tip: open the HTML report in a browser and use File → Print → Save as PDF."
            )
            return False

        html_str = self.to_html(embed_images=True, figures_dir=figures_dir)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        _WeasyprintHTML(string=html_str).write_pdf(output_path)
        print(f"PDF report saved:      {output_path}")
        return True

    def export_all(
        self,
        output_dir: str = ".",
        base_name: str = "ltem_report",
        figures_dir: Optional[str] = None,
    ) -> Dict[str, Optional[str]]:
        """
        Export the report in all three formats: Markdown, HTML, and PDF.

        Parameters
        ----------
        output_dir : str
            Directory where the output files will be saved.
        base_name : str
            File name stem (without extension). Default: 'ltem_report'.
        figures_dir : str, optional
            Base directory for resolving relative image paths in figures.
            Defaults to output_dir.

        Returns
        -------
        dict
            {'md': path, 'html': path, 'pdf': path or None}

        Example
        -------
            paths = report.export_all(
                output_dir="my_analysis/",
                base_name="ltem_temporal_report",
                figures_dir="my_analysis/figures"
            )
            print(paths)
            # {'md': 'my_analysis/ltem_temporal_report.md',
            #  'html': 'my_analysis/ltem_temporal_report.html',
            #  'pdf': 'my_analysis/ltem_temporal_report.pdf'}
        """
        os.makedirs(output_dir, exist_ok=True)
        fdir = figures_dir or output_dir

        md_path   = os.path.join(output_dir, f"{base_name}.md")
        html_path = os.path.join(output_dir, f"{base_name}.html")
        pdf_path  = os.path.join(output_dir, f"{base_name}.pdf")

        self.generate(output_path=md_path)
        self.to_html(output_path=html_path, figures_dir=fdir)
        pdf_ok = self.to_pdf(output_path=pdf_path, figures_dir=fdir)
        req_path = self._write_requirements(output_dir)

        return {
            "md":           md_path,
            "html":         html_path,
            "pdf":          pdf_path if pdf_ok else None,
            "requirements": req_path,
        }

    @staticmethod
    def _write_requirements(output_dir: str) -> str:
        """Write requirements.txt to output_dir."""
        req_path = os.path.join(output_dir, "requirements.txt")
        content = (
            "# chatMPA Studio – analysis requirements\n"
            "# Install: pip install -r requirements.txt\n"
            "# PDF support: pip install chatmpa[pdf]  (requires: brew install pango)\n\n"
            "# Core analysis\n"
            "pandas\n"
            "numpy\n"
            "scipy\n"
            "matplotlib\n"
            "seaborn\n"
            "\n# Report generation\n"
            "markdown\n"
            "tabulate\n"
            "\n# PDF export (optional)\n"
            "# weasyprint\n"
            "\n# chatMPA report module (install once from repo)\n"
            "# pip install -e /path/to/chatmpa-studio/python/\n"
        )
        with open(req_path, "w") as f:
            f.write(content)
        print(f"Requirements saved:    {req_path}")
        return req_path


# =============================================================================
# HELPER FUNCTIONS FOR COMMON REPORT SECTIONS
# =============================================================================

def generate_environmental_context(
    df: pd.DataFrame,
    sst_col: str = "mean_sst",
    chl_col: str = "mean_chl",
    year_col: str = "year",
) -> str:
    """Generate an environmental context section with SST and Chl-a statistics."""
    sst_mean = df[sst_col].mean()
    sst_min  = df[sst_col].min()
    sst_max  = df[sst_col].max()
    chl_mean = df[chl_col].mean()
    chl_min  = df[chl_col].min()
    chl_max  = df[chl_col].max()
    annual_sst = df.groupby(year_col)[sst_col].mean()

    return (
        f"La temperatura superficial del mar (SST) en la región de estudio presentó "
        f"variabilidad interanual entre {annual_sst.index.min()} y {annual_sst.index.max()}, "
        f"con valores que fluctuaron entre {sst_min:.1f}°C y {sst_max:.1f}°C "
        f"(promedio: {sst_mean:.1f}°C).\n\n"
        f"La concentración promedio de clorofila-a mostró valores entre "
        f"{chl_min:.2f} y {chl_max:.2f} mg/m³ (promedio: {chl_mean:.2f} mg/m³).\n\n"
        f"| Variable | Mínimo | Máximo | Promedio |\n"
        f"|----------|--------|--------|----------|\n"
        f"| SST (°C) | {sst_min:.1f} | {sst_max:.1f} | {sst_mean:.1f} |\n"
        f"| Chl-a (mg/m³) | {chl_min:.2f} | {chl_max:.2f} | {chl_mean:.2f} |\n\n"
    )


def generate_fish_community_section(
    df: pd.DataFrame,
    biomass_col: str = "biomass",
    species_col: str = "species",
    region_col: str = "region",
    year_col: str = "year",
) -> str:
    """Generate a fish community overview section."""
    total_species = df[species_col].nunique()
    total_biomass = df[biomass_col].sum()
    regional_bio  = df.groupby(region_col)[biomass_col].sum()
    top_region    = regional_bio.idxmax()

    content = (
        f"Se registraron un total de **{total_species}** especies con una biomasa "
        f"acumulada de **{total_biomass:.2f} ton/ha**. "
        f"La región con mayor biomasa fue **{top_region}** ({regional_bio[top_region]:.2f} ton/ha).\n\n"
        f"#### Biomasa por región\n\n"
        f"| Región | Biomasa Total (ton/ha) |\n"
        f"|--------|----------------------|\n"
    )
    for region, biomass in regional_bio.items():
        content += f"| {region} | {biomass:.2f} |\n"
    return content + "\n"


def generate_trophic_structure_section(
    df: pd.DataFrame,
    biomass_col: str = "biomass",
    trophic_col: str = "trophic_level",
) -> str:
    """Generate a trophic structure section."""
    def assign_group(tl):
        if tl < 2.5:   return "Herbívoros"
        elif tl < 3.5: return "Omnívoros"
        elif tl < 4.0: return "Carnívoros"
        else:           return "Depredadores tope"

    df2 = df.copy()
    df2["trophic_group"] = df2[trophic_col].apply(assign_group)
    trophic_bio = df2.groupby("trophic_group")[biomass_col].sum()
    total = trophic_bio.sum()

    content = (
        "La estructura funcional del ensamble de peces muestra la distribución "
        "de biomasa entre los diferentes niveles tróficos:\n\n"
        "| Grupo Trófico | Biomasa (ton/ha) | Proporción (%) |\n"
        "|---------------|------------------|----------------|\n"
    )
    for group, bio in trophic_bio.items():
        content += f"| {group} | {bio:.2f} | {bio/total*100:.1f} |\n"
    content += f"\n**Biomasa total:** {total:.2f} ton/ha\n\n"
    return content


def generate_conclusion_section(
    key_findings: List[str],
    recommendations: List[str],
    language: str = "es",
) -> str:
    """Generate a conclusion section with numbered key findings and recommendations."""
    if language == "es":
        findings_header = "### Hallazgos principales"
        recs_header     = "### Recomendaciones"
    else:
        findings_header = "### Key Findings"
        recs_header     = "### Recommendations"

    content = f"{findings_header}\n\n"
    for i, finding in enumerate(key_findings, 1):
        content += f"{i}. {finding}\n\n"
    content += f"\n{recs_header}\n\n"
    for i, rec in enumerate(recommendations, 1):
        content += f"{i}. {rec}\n\n"
    return content


# =============================================================================
# LOADING HELPER  (use this in skill scripts instead of sys.path hacks)
# =============================================================================

def load_report_template(custom_path: Optional[str] = None):
    """
    Load this module from a skill script without needing sys.path manipulation.

    Usage in any skill script
    -------------------------
        import importlib.util, os
        _HERE = os.path.dirname(os.path.abspath(__file__))
        _TMPL = os.path.normpath(os.path.join(
            _HERE, '../ltem-fish-community/references/report_template.py'))
        spec = importlib.util.spec_from_file_location('report_template', _TMPL)
        rt   = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rt)
        LTEMReportGenerator = rt.LTEMReportGenerator

    Or simply hardcode the absolute path:
        _TMPL = os.path.expanduser(
            '~/Projects/chatmpa-studio/.claude/skills/'
            'ltem-fish-community/references/report_template.py')
    """
    pass  # Documentation only — see docstring above.


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_report():
    """Demonstrate full multi-format report export."""
    report = LTEMReportGenerator(
        title="Informe de Monitoreo Ecológico",
        region="Parque Nacional Cabo Pulmo",
        period="Primavera-Otoño 2025",
        language="es",
    )
    report.add_author("Eduardo León Solórzano", "M.C.", "CBMC", "author")
    report.add_author("Fabio Favoretto", "Ph.D.", "CBMC", "author")

    report.add_section(
        "Contexto ambiental",
        "La temperatura superficial del mar presentó variabilidad interanual...",
        "results",
    )
    report.add_section(
        "Conclusión",
        generate_conclusion_section(
            key_findings=["Cabo Pulmo mantiene una de las biomasas más altas del golfo."],
            recommendations=["Continuar el monitoreo para detectar cambios a largo plazo."],
        ),
        "conclusion",
    )
    report.add_reference(
        "Aburto-Oropeza, O., et al. (2011). Large recovery of fish biomass. PLoS ONE."
    )

    # ── Single call generates .md, .html, and .pdf ──
    paths = report.export_all(
        output_dir="example_report/",
        base_name="ltem_example",
        figures_dir="example_report/figures",
    )
    print("Generated files:", paths)
    return paths


if __name__ == "__main__":
    example_report()
