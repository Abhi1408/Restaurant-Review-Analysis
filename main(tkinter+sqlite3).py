import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from tkinter import *

# Download NLTK stopwords data
nltk.download('stopwords')

# Global variables
rras_code = "Wyd^H3R"
food_rev = {}
food_perc = {}

# Initialize the database
def initialize_database():
    conn = sqlite3.connect('Restaurant_food_data.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS item (Item_name text, No_of_customers text, "
              "No_of_positive_reviews text, No_of_negative_reviews text, Positive_percentage text, "
              "Negative_percentage text)")
    conn.commit()
    conn.close()

# Initialize the restaurant data
def initialize_data(foods):
    conn = sqlite3.connect('Restaurant_food_data.db')
    c = conn.cursor()
    for i in range(len(foods)):
        c.execute("INSERT INTO item VALUES(:item_name, :no_of_customers, :no_of_positives, "
                  ":no_of_negatives, :pos_perc, :neg_perc)",
                  {
                      'item_name': foods[i],
                      'no_of_customers': "0",
                      'no_of_positives': "0",
                      'no_of_negatives': "0",
                      'pos_perc': "0.0%",
                      'neg_perc': "0.0%"
                  }
                  )
    conn.commit()
    conn.close()

# User interface for giving reviews
def take_review(foods):
    root2 = Toplevel()
    root2.title("Restaurant Review Analysis System - Give Review")

    def submit_review():
        review_text = review_entry.get()
        estimate_review(review_text, selected_food, foods)
        review_entry.delete(0, END)
        result_label.config(text="Review submitted successfully!")

    selected_food = StringVar()
    selected_food.set(foods[0])  # Default to the first food item

    food_label = Label(root2, text="Select the food item:")
    food_menu = OptionMenu(root2, selected_food, *foods)
    review_label = Label(root2, text="Enter your review:")
    review_entry = Entry(root2, width=50)
    submit_button = Button(root2, text="Submit Review", command=submit_review)
    result_label = Label(root2, text="")

    food_label.grid(row=0, column=0, padx=10, pady=10)
    food_menu.grid(row=0, column=1, padx=10, pady=10)
    review_label.grid(row=1, column=0, padx=10, pady=10)
    review_entry.grid(row=1, column=1, padx=10, pady=10)
    submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    result_label.grid(row=3, column=0, columnspan=2)

# User interface for owner verification
def login():
    root3 = Toplevel()
    root3.title("Restaurant Review Analysis System - Owner Verification")
    
    def owner_login():
        # Add owner login logic here
        owner_username = username_entry.get()
        owner_password = password_entry.get()
        # Perform owner verification here, e.g., check credentials in a database
        
        if owner_username == "Abhi" and owner_password == "Govil":
            access_data(foods)
            root3.destroy()
        else:
            login_result_label.config(text="Invalid credentials. Please try again.")
            username_entry.delete(0, END)
            password_entry.delete(0, END)
    
    username_label = Label(root3, text="Username:")
    password_label = Label(root3, text="Password:")
    username_entry = Entry(root3, width=30)
    password_entry = Entry(root3, width=30, show="*")  # Masking the password
    login_button = Button(root3, text="Login", command=owner_login)
    login_result_label = Label(root3, text="")

    username_label.grid(row=0, column=0, padx=10, pady=10)
    password_label.grid(row=1, column=0, padx=10, pady=10)
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)
    login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    login_result_label.grid(row=3, column=0, columnspan=2)

# User interface for accessing and managing restaurant data
def access_data(foods):
    root5 = Toplevel()
    root5.title("Restaurant Review Analysis System - Restaurant Database")

    def clear_all_data():
        clear_all_item_data()
        access_data(foods)

    def clear_selected_data():
        selected_items = [foods[i] for i in range(len(foods)) if variables[i].get() == 1]
        clear_item_data(selected_items)
        access_data(foods)

    data_label = Label(root5, text="Restaurant Data Management", font=('Arial', 18, 'bold', 'underline'))
    clear_all_button = Button(root5, text="Clear All Data", command=clear_all_data, font=('Arial', 14))
    clear_selected_button = Button(root5, text="Clear Selected Data", command=clear_selected_data, font=('Arial', 14))
    back_button = Button(root5, text="Back to Main Menu", command=root5.destroy, font=('Arial', 14))

    data_label.grid(row=0, column=0, columnspan=2, pady=10)
    clear_all_button.grid(row=1, column=0, columnspan=2, pady=10)
    clear_selected_button.grid(row=2, column=0, columnspan=2, pady=10)
    back_button.grid(row=3, column=0, columnspan=2)

    for i, food in enumerate(foods):
        var = IntVar()
        chk = Checkbutton(root5, text=food, variable=var, onvalue=1, offvalue=0)
        chk.grid(row=i + 4, column=0, columnspan=2)

# Function to clear all item data
def clear_all_item_data():
    # Clear all item data
    conn = sqlite3.connect('Restaurant_food_data.db')
    c = conn.cursor()
    for food in foods:
        c.execute("""UPDATE item SET Item_name = :item_name, No_of_customers = :no_of_customers, 
                     No_of_positive_reviews = :no_of_positives, No_of_negative_reviews = :no_of_negatives, 
                     Positive_percentage = :pos_perc, Negative_percentage = :neg_perc WHERE oid = :oid""",
                  {
                      'item_name': food,
                      'no_of_customers': "0",
                      'no_of_positives': "0",
                      'no_of_negatives': "0",
                      'pos_perc': "0.0%",
                      'neg_perc': "0.0%",
                      'oid': foods.index(food) + 1
                  })
    conn.commit()
    conn.close()

# Function to clear specific item data
def clear_item_data(selected_foods):
    # Clear data for selected items
    conn = sqlite3.connect('Restaurant_food_data.db')
    c = conn.cursor()
    for food in selected_foods:
        c.execute("""UPDATE item SET Item_name = :item_name, No_of_customers = :no_of_customers, 
                     No_of_positive_reviews = :no_of_positives, No_of_negative_reviews = :no_of_negatives, 
                     Positive_percentage = :pos_perc, Negative_percentage = :neg_perc WHERE oid = :oid""",
                  {
                      'item_name': food,
                      'no_of_customers': "0",
                      'no_of_positives': "0",
                      'no_of_negatives': "0",
                      'pos_perc': "0.0%",
                      'neg_perc': "0.0%",
                      'oid': foods.index(food) + 1
                  })
    conn.commit()
    conn.close()

# Function to estimate reviews and update restaurant data
def estimate_review(s, selected_food, foods):
    conn = sqlite3.connect('Restaurant_food_data.db')
    c = conn.cursor()
    review = re.sub('[^a-zA-Z]', ' ', s).lower().split()
    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    all_stopwords.remove('not')
    
    review = [ps.stem(word) for word in review if word not in set(all_stopwords)]
    review = ' '.join(review)
    
    X = cv.transform([review]).toarray()
    res = classifier.predict(X)[0]
    
    if "not" in review:
        res = abs(res - 1)
    
    c.execute("SELECT *, oid FROM item")
    records = c.fetchall()
    
    for rec in records:
        rec_list = list(rec)
        if rec_list[0] == selected_food:
            n_cust = int(rec_list[1]) + 1
            n_pos = int(rec_list[2])
            n_neg = int(rec_list[3])
            
            if res == 1:
                n_pos += 1
            else:
                n_neg += 1
                
            pos_percent = round((n_pos / n_cust) * 100, 1)
            neg_percent = round((n_neg / n_cust) * 100, 1)
            c.execute("""UPDATE item SET Item_name = :item_name, No_of_customers = :no_of_customers, 
                         No_of_positive_reviews = :no_of_positives, No_of_negative_reviews = :no_of_negatives, 
                         Positive_percentage = :pos_perc, Negative_percentage = :neg_perc WHERE oid = :oid""",
                      {
                          'item_name': rec_list[0],
                          'no_of_customers': str(n_cust),
                          'no_of_positives': str(n_pos),
                          'no_of_negatives': str(n_neg),
                          'pos_perc': str(pos_percent) + "%",
                          'neg_perc': str(neg_percent) + "%",
                          'oid': foods.index(rec_list[0]) + 1
                      }
                      )
    
    conn.commit()
    conn.close()

# Main entry point
if __name__ == "__main__":
    # Define the list of foods
    foods = ["Idly", "Dosa", "Vada", "Roti", "Meals", "Veg Biryani",
             "Egg Biryani", "Chicken Biryani", "Mutton Biryani",
             "Ice Cream", "Noodles", "Manchurian", "Orange juice",
             "Apple Juice", "Pineapple juice", "Banana juice", "Appam"]
    
    # Load dataset and create the corpus
    dataset = pd.read_csv(r'C:\Users\A\Desktop\Restaurant_Reviews.tsv',delimiter='\t', quoting=3)
    corpus = []

    for i in range(1000):
        review = re.sub('[^a-zA-Z]', ' ', dataset['Review'][i])
        review = review.lower().split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        
        review = [ps.stem(word) for word in review if word not in set(all_stopwords)]
        review = ' '.join(review)
        corpus.append(review)

    # Create a CountVectorizer and transform the corpus into features
    cv = CountVectorizer(max_features=1500)
    X = cv.fit_transform(corpus).toarray()
    y = dataset.iloc[:, -1].values

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

    # Create a Gaussian Naive Bayes classifier and fit it to the data
    classifier = GaussianNB()
    classifier.fit(X_train, y_train)

    # Create the main UI
    root1 = Tk()
    root1.title("Restaurant Review Analysis System - Welcome Page")

    label = Label(root1, text="RESTAURANT REVIEW ANALYSIS SYSTEM", bd=2, font=('Arial', 47, 'bold', 'underline'))
    ques = Label(root1, text="Are you a Customer or Owner ?")
    cust = Button(root1, text="Customer", font=('Arial', 20), padx=80, pady=20, command=lambda: take_review(foods))
    owner = Button(root1, text="Owner", font=('Arial', 20), padx=100, pady=20, command=login)

    label.grid(row=0, column=0)
    ques.grid(row=1, column=0, sticky=W+E)
    ques.config(font=("Helvetica", 30))
    cust.grid(row=2, column=0)
    owner.grid(row=3, column=0)

    # Start the main application loop
    root1.attributes("-fullscreen", True)
    root1.mainloop()
