# 🎈 Blank app template

Overall structure:

1. Load a set of starting PDFs into "raw" directory.
2. For each of the "raw" PDFs:
  a. Read PDF
  b. Obtain the list of references from PDF.
  c. Put each reference in a separate file in "raw-references" directory.
  d. Move PDF to "processed" directory.
3. For each PDF in "raw-references" directory:
   a. Try to find the PDF file on the web.
   b. If successful, add to "raw-to-download" directory.
   c. Move reference to "ref-success" or "ref-fail" directories
4. For each PDF in "raw-to-download" directory:
   a. Try to find the PDF file on the web.
   b. If successful, add to "raw" directory.
   c. Move reference to "download-success" or "download-fail" directories
