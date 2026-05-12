# ----------------------------------------------------
# PDF REPORT DOWNLOAD (FIXED)
# ----------------------------------------------------

st.markdown("## 📄 Download Complete Report")

if st.button("⬇️ Generate PDF Report"):

    pdf = FPDF()
    pdf.add_page()

    # Use only standard fonts
    pdf.set_font("Arial", 'B', 18)

    # Title
    pdf.cell(
        200,
        10,
        txt="AgriSmart Pro - Crop Analysis Report",
        ln=True,
        align='C'
    )

    pdf.ln(10)

    # Date
    pdf.set_font("Arial", '', 12)

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M')

    pdf.cell(
        200,
        10,
        txt=f"Generated on: {current_time}",
        ln=True
    )

    pdf.ln(5)

    # Soil Parameters
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Soil Parameters", ln=True)

    pdf.set_font("Arial", '', 12)

    pdf.cell(200, 8, txt=f"Nitrogen (N): {N}", ln=True)
    pdf.cell(200, 8, txt=f"Phosphorus (P): {P}", ln=True)
    pdf.cell(200, 8, txt=f"Potassium (K): {K}", ln=True)
    pdf.cell(200, 8, txt=f"Soil pH: {ph}", ln=True)

    pdf.ln(5)

    # Environmental Conditions
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Environmental Conditions", ln=True)

    pdf.set_font("Arial", '', 12)

    pdf.cell(200, 8, txt=f"Temperature: {temp} C", ln=True)
    pdf.cell(200, 8, txt=f"Humidity: {hum} percent", ln=True)
    pdf.cell(200, 8, txt=f"Rainfall: {rain} mm", ln=True)

    pdf.ln(5)

    # Crop Predictions
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Top Crop Predictions", ln=True)

    pdf.set_font("Arial", '', 12)

    for crop, p in st.session_state['res']:

        pdf.cell(
            200,
            8,
            txt=f"{crop} - {p*100:.1f}% Match",
            ln=True
        )

    pdf.ln(5)

    # Insurance
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Insurance Recommendation", ln=True)

    pdf.set_font("Arial", '', 12)

    pdf.cell(
        200,
        8,
        txt=f"Annual Premium: Rs. {int(prem)}",
        ln=True
    )

    pdf.cell(
        200,
        8,
        txt=f"Sum Insured: Rs. {int(total)}",
        ln=True
    )

    pdf.ln(10)

    pdf.multi_cell(
        0,
        8,
        txt="Recommended Government Scheme: Pradhan Mantri Fasal Bima Yojana"
    )

    # Save PDF
    pdf_output = "AgriSmart_Report.pdf"

    pdf.output(pdf_output)

    # Download Button
    with open(pdf_output, "rb") as pdf_file:

        st.download_button(
            label="Download Complete Report",
            data=pdf_file,
            file_name="AgriSmart_Report.pdf",
            mime="application/pdf"
        )

    st.success("PDF Report Generated Successfully!")
