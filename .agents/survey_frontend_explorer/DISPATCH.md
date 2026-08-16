## 2026-08-16T19:19:05Z

You are the Frontend Structure Explorer for the Binary Options Quantitative Terminal UI/UX Redesign project.
Your working directory is: c:\Users\juanc\Desktop\prueba\.agents\survey_frontend_explorer\

You MUST read:
1. c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
2. All frontend templates, HTML files, CSS stylesheets, and JS scripts across c:\Users\juanc\Desktop\prueba (e.g. templates/, static/, or root).

Your task is to perform an exhaustive survey of the existing frontend codebase and catalog:
1. File structure: All HTML/Jinja2 templates, CSS stylesheets, JS files, and third-party library imports (CDNs, local scripts like TradingView Lightweight Charts, Chart.js, Tailwind/Bootstrap/custom CSS).
2. Complete DOM Element Catalog:
   - Every single HTML element ID (e.g., form inputs, control buttons, tab buttons, modal containers, chart containers, metric display spans/divs, table bodies).
   - Every form input name, type, default value, and data attribute.
   - Every button ID, class, and onclick / event handler binding.
3. JavaScript Architecture:
   - Script files and their responsibilities.
   - Event listeners attached via document.getElementById, addEventListener, jQuery, or inline handlers.
   - Dynamic DOM manipulation, template rendering, WebSocket message handlers, or fetch/AJAX API calls.
   - Any global state variables or objects.
4. Existing layout and CSS structure:
   - Current layout containers, grid/flex structure, CSS classes, responsive breakpoints.
5. Critical Preservation Inventory:
   - The exact list of all IDs, input names, and JS hooks that MUST remain 100% preserved to guarantee zero regressions.

Write your comprehensive report to:
c:\Users\juanc\Desktop\prueba\.agents\survey_frontend_explorer\survey_frontend_report.md
and write a standard handoff.md in your working directory.
When finished, send a message to the caller with the summary and path to your report.
