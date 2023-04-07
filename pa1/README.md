## How to Set Up

Follow the instructions below to set up the project:

1. Ensure that you have Python 3.10.x installed on your system.
2. Install the required packages using `pip`. You can do this by running the following command in your terminal:

    ```sh
    pip install -r requirements.txt
    ```

   This command will install all required packages from the `requirements.txt` file. Note that the packages listed below are not present by default, so they need to be installed separately:

   - `validators`
   - `crawldb_model`
   - `Flask`
   - `flask_httpauth`
   - `tldextract`
   - `requests`
   - `selenium`
   - `bs4`

3. Run `server.py` using the following command:

    ```sh
    python server.py
    ```

   This will start the Flask server at http://127.0.0.1:8000/.

4. Run `client_demo_multithread.py` to run the client demo.