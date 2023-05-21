## How to Set Up

Follow the instructions below to set up the project:

1. Ensure that you have Python 3.10.x installed on your system.
2. Install the required packages using `pip`. You can do this by running the following command in your terminal:

    ```sh
    pip install -r requirements.txt
    ```

   This command will install all required packages from the `requirements.txt` file. Note that the packages listed below are not present by default, so they need to be installed separately:

   - `html2text`
   - `lxml`


3. Go to `implementation-extraction` folder and run `run-extraction.py` using the following command:

    ```sh
    python run-extraction.py [A|B|C]
    ```

   Where A, B and C represent different extraction algorithms. A for regex, B for xpath and C for Road runner.