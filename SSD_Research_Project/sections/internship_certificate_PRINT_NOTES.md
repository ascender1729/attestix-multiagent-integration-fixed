# Printing the Internship Certificate

The certificate page is rendered fully in LaTeX with the statutory
letterhead block (Section 12(3), Companies Act 2013). For the
final hardbinding, you have two equivalent options:

## Option A - Sign the LaTeX-rendered page directly (simplest)

1. Compile the report on Overleaf. The certificate appears immediately
   after the NIT Patna academic certificate, before the Declaration.
2. Print the entire report on plain bond paper for binding.
3. After printing, physically:
   - sign the signature line above your name on the certificate page
   - affix the VibeTensor company seal in the marked area
4. Hand over to the hardbinder. The bound copy will have a signed and
   sealed certificate as page (vi) or thereabouts.

## Option B - Replace the LaTeX page with a scanned letterhead copy (more formal)

If NIT Patna's project committee expects the certificate to be on
the company's actual pre-printed letterhead paper:

1. Compile and print the report MINUS the certificate page (comment out
   `\input{sections/internship_certificate}` in `main.tex` before the
   final compile).
2. Separately, take a sheet of VibeTensor pre-printed letterhead
   stationery and:
   - Either: print the body text of the certificate onto the letterhead
     paper using a normal office printer (set printer to NOT print the
     header / footer since letterhead already has them).
   - Or: type / re-type the body of the certificate into a Word document
     formatted to fit the letterhead, then print onto the letterhead.
3. Sign the certificate by hand on the printed letterhead copy.
4. Affix the VibeTensor company seal.
5. Insert the signed letterhead certificate as an insert page in the
   correct position when handing the report to the hardbinder. Tell the
   hardbinder which page number it should sit at (so the table of
   contents on the LaTeX-printed pages still reflects it).

## Audit checklist before signing

Per the VibeTensor drafting framework (audit clauses H.1-H.8):

- [ ] Letterhead has all Section 12(3) Companies Act 2013 mandatory fields
      (company name, registered office, CIN, email, website). Check.
- [ ] Document identifier present (`VT/INTC/2026/SP-2206119`) per
      ISO 9001:2015 clause 7.5.2. Check.
- [ ] Date of issue is in the past or equal to today; not back-dated more
      than the actual sign-off date. Update `Date of Issue` in the .tex if needed.
- [ ] Internship period dates match the executed offer letter on file
      (`05 January 2026 to 27 June 2026`).
- [ ] Intern's full legal name, roll number and institution match the
      NIT Patna academic certificate verbatim.
- [ ] Intellectual-property statement is consistent with the executed IP
      assignment agreement (item H-4 from the audit). If the IP assignment
      is not yet signed, hold the certificate until it is - the IP statement
      in this certificate assumes that agreement is in force.
- [ ] No claim of ISO certification ("certified per ISO 9001") - only
      "aligned with ISO 9001:2015". Check.
- [ ] No reference to NIT Patna in any external copy of this certificate.
      External-scrubbed variant uses a placeholder page only.

## What you cannot do

- Issue this certificate before the IP-assignment agreement (H-4) is signed
  by both parties. The IP statement explicitly references the executed
  assignment; back-dating the certificate to a date before the assignment
  was signed creates a documentary inconsistency that any reviewer can
  spot.
- Issue the certificate without the company seal. NIT Patna's committee
  routinely verifies the seal when internship certificates are involved.
