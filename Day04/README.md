

# Differential Equation Visualizer

## About the Project

For this assignment, I created a web application using Flask, based on my previous Python project that visualizes differential equations through slope fields.

The goal was to take the mathematical calculations from my original program and make them accessible through an interactive web interface.

Users can enter a differential equation, optionally provide an initial condition, and generate a slope field showing the direction of possible solutions. When an initial condition is provided, the application also plots the corresponding numerical solution.

## How I Built It

I started by adapting the code from my previous assignment.

The original program accepted user input through the Python terminal and displayed graphs using Matplotlib.

To turn it into a web application, I separated the mathematical calculations from the user interface.

I organized the project into the following files:

- **`slope_logic.py`** — Contains the mathematical calculations, including parsing equations, generating slope fields, and solving differential equations using the fourth-order Runge–Kutta (RK4) method.
- **`app.py`** — Uses Flask to connect the mathematical functions to the website. It receives user input and returns the generated graph.
- **`templates/index.html`** — Defines the webpage where users enter their equations and view the results.
- **`static/style.css`** — Controls the visual design of the website.
- **`requirements.txt`** — Lists the Python libraries required to run the application.

## Libraries Used

- **Flask:** Creates the web application and handles user input.
- **NumPy:** Performs numerical calculations and creates the grid for the slope field.
- **SymPy:** Interprets mathematical expressions entered by the user.
- **Matplotlib:** Generates the slope-field plots and solution curves.
- **AST:** Helps interpret mathematical expressions while restricting the accepted Python syntax.

## How the Application Works

1. The user enters a differential equation, such as `x - y`.
2. The application interprets the expression using SymPy.
3. NumPy calculates the slope at different points on a grid.
4. Matplotlib generates a slope-field visualization.
5. If the user provides an initial condition, the RK4 method calculates an approximate solution.
6. Flask displays the resulting graph on the webpage.

## How to Run the Application

First, install the required libraries:

```bash
pip install -r requirements.txt
```

Then start the Flask application:

```bash
python app.py
```

Open the following address in your browser:

http://127.0.0.1:5000

You can now enter equations and generate their slope fields.

## What I Learned

This assignment helped me understand how to turn an existing Python program into a web application.

In particular, I learned how to separate the mathematical logic from the user interface, use Flask to handle input from a webpage, and display Python-generated graphs in a browser.

All of this was completed following instructions from ChatGPT, who guided me through the steps and wrote the code for me.
