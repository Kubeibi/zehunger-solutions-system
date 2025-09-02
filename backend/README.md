# BSF Farm Waste Management - Python Backend

This backend is built with Flask and connects to a MySQL database to store data from the waste management frontend.



1.  **Prerequisites**:
    *   Python 3.7+ installed.
    *   MySQL server installed and running.
    *   Access to a MySQL client (e.g., MySQL Workbench, DBeaver, or command line) to create the database and tables.

2.  **Create a Virtual Environment** (recommended):
    Navigate to the `waste-management-app/backend` directory in your terminal:
    ```bash
    cd path/to/your/workspace/waste-management-app/backend
    ```
    Create a virtual environment:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   Windows: `.\venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies**:
    With the virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Database Connection**:
    *   Open `config.py`.
    *   Update `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` with your MySQL server details and desired database name.
    ```python
    # Example config.py
    DB_HOST = 'localhost'
    DB_USER = 'your_user'
    DB_PASSWORD = 'your_password'
    DB_NAME = 'bsf_farm_db' # This database must exist on your MySQL server
    ```

5.  **Create Database and Tables in MySQL**:
    *   Connect to your MySQL server using your preferred client.
    *   Create the database specified in `config.py` if it doesn't already exist:
        ```sql
        CREATE DATABASE IF NOT EXISTS bsf_farm_db;
        USE bsf_farm_db;
        ```
    *   Create the necessary tables. For the "Waste Sourcing" form, the table might look like this:
        ```sql
        CREATE TABLE IF NOT EXISTS waste_sourcing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            collection_date DATE NOT NULL,
            collection_time TIME NOT NULL,
            source_type VARCHAR(100) NOT NULL,
            source_name VARCHAR(255) NOT NULL,
            waste_type VARCHAR(100) NOT NULL,
            waste_weight_kg DECIMAL(10, 2) NOT NULL,
            segregation_status VARCHAR(50) NOT NULL,
            collection_personnel VARCHAR(255) NOT NULL,
            contaminants_found TEXT, -- Comma-separated string or consider a separate table for many-to-many
            notes TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
    *   You will need to define and create similar tables for `storage_records`, `processing_records`, and `environmental_monitoring` based on the fields in your `Waste.html` forms.

6.  **Run the Flask Application**:
    Ensure your virtual environment is activated and you are in the `waste-management-app/backend` directory.
    ```bash
    python app.py
    ```
    The application will start, typically on `http://127.0.0.1:5000/`. You'll see log messages in the console, including connection status to the database.

## API Endpoints

The following endpoints are planned/implemented:

*   `POST /api/waste-sourcing`: Records data from the Waste Sourcing form.
*   `POST /api/storage-records`: (To be implemented) Records data from the Storage Records form.
*   `POST /api/processing-records`: (To be implemented) Records data from the Processing Records form.
*   `POST /api/environmental-monitoring`: (To be implemented) Records data from the Environmental Monitoring form.

## Next Steps

1.  **Implement Remaining Endpoints**: Add route handlers in `app.py` for the other forms (`storage-records`, `processing-records`, `environmental-monitoring`).
2.  **Define and Create Database Tables**: For each new endpoint, define the corresponding MySQL table structure and create it.
3.  **Enhance Validation**: Add more robust server-side validation for incoming data in each endpoint.
4.  **Error Handling**: Improve error handling and logging.
5.  **Frontend Integration**: Ensure your `Waste.html` JavaScript `fetch` calls are correctly pointing to these backend endpoints (e.g., `http://127.0.0.1:5000/api/waste-sourcing`). Update the `endpoint` variable in the `setupForm` function in your `Waste.html`.
6.  **Security**: Consider security best practices, especially if this application will be exposed to the internet (e.g., input sanitization, environment variables for sensitive configs). 

## Deployment Environment Variables

Set these variables in your managed hosting dashboard (Render/Railway):

- DB_HOST
- DB_USER
- DB_PASSWORD
- DB_NAME
- SECRET_KEY
- EMAIL_HOST (default smtp.gmail.com)
- EMAIL_PORT (default 587)
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- ADMIN_EMAIL
- API_BASE_URL (e.g., https://api.efarmzehunger.com)
- API_DEBUG (true/false) 