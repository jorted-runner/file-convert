# Overview

This project is a client-server networking program that facilitates file transfer and conversion between a client and server. The client can upload files to the server, which processes and converts them (e.g., to PDF format) before sending the results back to the client. The primary goal of this software is to deepen my understanding of socket programming, networking, and file handling in Python.
{Provide a description the networking program that you wrote. Describe how to use your software.  If you did Client/Server, then you will need to describe how to start both.}

The program allows the user to:

1. See available files on the server.
2. Upload files from the client to the server.
3. Download files from the server to the client.
4. Convert individual files or entire directories of files to PDF format.

To run this software, you need to start both the server and client programs, which will establish a connection for communication and file transfer.

[Software Demo Video](http://youtube.link.goes.here)---

## Network Communication

This program follows a **client-server architecture** using the **TCP protocol** for reliable communication. The default port used for the connection is **5050**.

### Message Format

1. **Metadata:** JSON-encoded strings sent to describe files (e.g., size, name).
2. **Binary Data:** Files are transferred as raw binary data in chunks of 1024 bytes.
3. **Acknowledgment Messages:** The server and client exchange simple messages like "ACK" to confirm successful receipt of data.

---

## Development Environment

- **Programming Language:** Python
- **Libraries Used:**
  - `socket` for networking.
  - `os` and `shutil` for file and directory management.
  - `json` for encoding and decoding metadata.
  - `fpdf` for PDF creation.
  - `Pillow` and `pillow_heif` for image processing.
- **Tools:** The program was developed and tested using Python 3 in a local environment.

### Setting up the Development Environment

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS & Linux:

   ```bash
   source venv/bin/activate
   ```

    - On Windows:

    ```bash
    .\\venv\\Scripts\\activate
    ```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Useful Websites

- [Python Official Documentation](https://docs.python.org/3/)
- [FPDF Documentation](https://pyfpdf.github.io/fpdf2/)
- [Python Pillow Documentation](https://pillow.readthedocs.io/)

---

## Future Work

- **Improve Error Handling:**
  - Handle cases where files are corrupted during transfer.
  - Address edge cases like interrupted connections or permission errors.
- **Support Additional Formats:**
  - Add functionality to convert more file types, such as `.docx` and `.msg`, into PDFs.
- **Optimize Large Transfers:**
  - Implement better chunking and resume functionality for large file transfers.
- **Add User Interface:**
  - Develop a graphical interface to make the software more user-friendly.
- **Security Enhancements:**
  - Implement encryption for file transfers to enhance security.
- **OCR PDF files:**
  - Add functionality to take scanned PDFs and convert them into OCRed PDFs to increase searchability of each file.
