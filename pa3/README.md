## How to Set Up

Follow the instructions below to set up the project:

1. Ensure that you have Python 3.10.x installed on your system.
2. Install the required packages using `pip`. You can do this by running the following command in your terminal:

    ```sh
    pip install -r requirements.txt
    ```

   This command will install all required packages from the `requirements.txt` file. Note that the packages listed below are not present by default, so they need to be installed separately:

   - `nltk`
   - `sqlite3`
   - `string`
   - `re`
   - `bs4`

3. Go to the `utils.py` file and uncomment (if not done previously) once these lines:

    ```sh
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    ```

After that 
