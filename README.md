# Moneyger
Terminal app to keep track of your personal spendings. Enjoy having full access 
to all your data. 

The app is written with python curses, uses SQLite database. 

Launch by running 
```
python main.py
```

---------------------------------------------------------
## The responsibilities of the main classes
### App
- inits the app, state manager, responsible for running the app, does actions based on a current state

### State Manager
- shifts between screens based on a current state

### SharedState 
- keeps track of the curret state

### Screen
- draws a screen
- handles a key
- returns a current state
