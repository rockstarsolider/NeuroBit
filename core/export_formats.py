# core/export_formats.py
from import_export.formats.base_formats import Format

class WeasyPDF(Format):
    def get_title(self):
        return "PDF"

    def get_extension(self):
        return "pdf"

    def can_import(self):
        return False

    def can_export(self):
        return True

    def is_available(self):
        try:
            import weasyprint  # noqa
            return True
        except Exception:
            return False

    def export_data(self, dataset, **kwargs):
        # Very simple HTML table; customize template if you like.
        from weasyprint import HTML
        headers = dataset.headers or []
        rows = dataset.dict  # list[dict]
        html_rows = "".join(
            "<tr>" + "".join(f"<td>{(r.get(h) or '')}</td>" for h in headers) + "</tr>"
            for r in rows
        )
        html = f"""
        <html><head><meta charset="utf-8" />
        <style>
          body {{ font-family: sans-serif; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 6px 8px; font-size: 12px; }}
          th {{ background: #f6f6f6; text-align: left; }}
        </style></head>
        <body>
          <h2>Subscriptions Export</h2>
          <table>
            <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
            <tbody>{html_rows}</tbody>
          </table>
        </body></html>
        """
        return HTML(string=html).write_pdf()
