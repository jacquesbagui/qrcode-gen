# QR Code Generator

This Flask application takes Excel files as input and generates QR codes for each row based on the vCard data extracted from the file. Users can download these QR codes individually or as a collection in a ZIP file for each session.

## Features

- **Upload Excel Files**: Users can upload an Excel file containing data to be encoded into QR codes.
- **Generate QR Codes**: For each entry in the Excel file, a QR code is generated.
- **Download Options**: Users can download a single QR code or all QR codes from a session in a ZIP file.
- **Session Management**: Track and manage different upload sessions with options to view or download past QR codes.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework.
- **SQLAlchemy**: SQL toolkit and ORM for database management.
- **SQLite**: Database used for storing session and QR code data.
- **QRCode Library**: Used for generating QR codes from data.
- **Tailwind CSS**: A utility-first CSS framework for styling.
- **Python 3**: Programming language used.

## Project Setup

Follow these instructions to set up and run the project locally.

### Prerequisites

- Python 3.8+
- pip
- virtualenv (optional but recommended for managing Python packages)

### Installation

1. **Clone the repository**

    ```bash
    git clone hhttps://github.com/jacquesbagui/qrcode-gen.git
    cd qrcode-gen
    ```

2. **Set up a virtual environment (recommended)**

    - Unix/MacOS:

      ```bash
      python -m venv venv
      source venv/bin/activate
      ```

    - Windows:

      ```cmd
      python -m venv venv
      .\venv\Scripts\activate
      ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Environment Variables**

    Set the necessary environment variables:

    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```

    Windows users can use `set` instead of `export`.

5. **Initialize the database**

    ```bash
    flask db upgrade
    ```

6. **Run the application**

    ```bash
    flask run
    ```

    Or for production environments:

    ```bash
    gunicorn -c gunicorn_config.py "app:app"
    ```

### Usage

- Open a web browser and navigate to `http://127.0.0.1:8000/` to access the application.
- Follow the on-screen instructions to upload an Excel file and generate QR codes.

## Contributing

Contributions are welcome! If you have suggestions or issues, please feel free to open an issue or create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

- Jean Jacques BAGUI - [jacques.bagui@gmail.com](mailto:jacques.bagui@gmail.com)
