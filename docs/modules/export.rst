Export Module
=============

Excel and PDF report generation.

.. automodule:: src.export
   :members:
   :undoc-members:
   :show-inheritance:

Excel Reports
-------------

.. autofunction:: src.export.create_excel_report

The Excel report contains four sheets:

1. **Summary**: Overall KPIs and metrics
2. **Evaporator Details**: Effect-by-effect data
3. **Crystallizer Details**: Batch results and crystal properties
4. **Heat Integration**: Pinch analysis and heat recovery

All sheets feature:

* Professional formatting with colored headers
* Borders and alignment
* Appropriate column widths
* Formulas and calculations

PDF Reports
-----------

.. autofunction:: src.export.create_pdf_report

The PDF report includes:

* **Title page** with project information
* **Evaporator results** with summary table
* **Effect-by-effect details** table
* **Crystallizer results** table
* **Optimization results** comparison
* **Heat Integration** analysis
* **Conclusions** with automated insights

Styling features:

* Custom colors matching brand theme
* Professional table styling
* Page breaks between sections
* Headers and footers
