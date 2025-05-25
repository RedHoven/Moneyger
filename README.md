# Moneyger
Terminal app to keep track of your personal spendings and have a completely full access to all your data. 

The app is written with python curses library and SQLite database. 

### Preview

![Moneyger Preview](https://raw.githubusercontent.com/redhoven/moneyger/main/preview/preview-grid.png)
<!-- ![Moneyger Preview](preview/preview-grid.png) -->

To start adding your transactions, enter the amount and press `Enter`. You can also add a description, category, and date. The app will automatically save your data to the database. To change the category, date or description, navigate to the line and press `i`. Press `Enter` to save changes and press `Enter` again to submit the transaction.

To switch to the analysis screen, press `s` (stats). Here you can see your spendings by categories, dates, and other statistics. You con return to the transactions screen by pressing `t` (transaction).

To exit the app, press `q` (quit).

### How to use?
1. Clone the repository:
   ```bash
   git clone
   ```

2. Navigate to the project directory:
   ```bash
    cd moneyger
    ```

3. Install the required dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

4. Run the app in the terminal:
    ```bash
    # Initialize the database when running for the first time
    python src/database.py --init 
    python src/main.py
    ```

> [!WARNING]  
> Make sure your terminal is sufficiently large to display the app properly. The recommended minimum size is 100x30 characters to be able to access all the screens. The app will not start if the terminal window is too small.

5. If the app suddenly breaks or something is not working properly, check the logs in moneyger.log file.

### 📁 Project Structure

📂 `src/`

* `app.py` — Initializes and runs the core application logic

* `main.py` — Entry point: boots the app and starts the main loop

* `state.py` — Defines the shared state of the application

* `state_manager.py` — Controls navigation between screens based on current state

* `screen_manager.py` — Builds and manages the different screens

* `keys.py` — Centralized key mappings for input handling

* `database.py` — Handles all data persistence and retrieval logic

* `stats.py` — Gathers and processes database stats for visual display

* `parsers.py` — Parses incoming input data into structured form

#### 📂 `screens/` — All screen definitions:

* `screen.py` — Abstract base class for all screens
* `main_screen.py` — Home screen for general interactions
* `extended_screen.py` — Transaction screen with history and guidance
* `analysis_screen.py` — Visualizes data insights and trends

### Component Responsibilities
App (`app.py`)
Orchestrates the entire application lifecycle. Initializes core modules and performs actions based on current shared state.

State Manager (`state_manager.py`)
Handles screen transitions by reacting to updates in the shared state.

Shared State (`state.py`)
Central storage for app state, enabling consistent and reactive behavior across screens.

Screen (`screens/*.py`)
Each screen:
- Renders its UI content
- Handles user key inputs
- Returns a potential new state

Statistics (stats.py)
Pulls data from the database and transforms it into display-ready insights.

Database (database.py)
Low-level data layer responsible for CRUD operations and persistent storage.
