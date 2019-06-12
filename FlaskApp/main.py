# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:15:42 2019

@author: v-cabad
"""

from flask import Flask, request, render_template
from cocktail_functions import generate_drink_output, generate_text, generate_textgenrnn_drink, \
    return_answers, vikram_generate_drink_output,vikram_generate_text
import sys
import os
from flask_bootstrap import Bootstrap
from textgenrnn import textgenrnn
import tensorflow as tf

import pyodbc 

# tell our app where our saved model is
sys.path.append(os.path.abspath("./models"))

from load import init_model

app = Flask(__name__)
Bootstrap(app)
# global vars for easy reusability
global model, graph, model2, graph2, model3, graph3, model4, graph4
# initialize these variables
model, graph = init_model('models/cocktail_model_json', "models/cocktail_model_weights.h5")
model2, graph2 = init_model('models/vik_model.json', "models/vik_model.h5")
model3 = textgenrnn(config_path="./models/textgenrnn_cocktail_config.json",weights_path="./models/textgenrnn_cocktail_weights.hdf5",vocab_path="./models/textgenrnn_cocktail_vocab.json")
graph3 = tf.get_default_graph()
model4 = textgenrnn(config_path="./models/textgenrnn_config.json",weights_path="./models/textgenrnn_weights.hdf5",vocab_path="./models/textgenrnn_vocab.json")
graph4 = tf.get_default_graph()
# prep PYODBC connection
global server, databasename, username, password
server = 'cocktail.database.windows.net' 
database = 'cocktaildb' 
username =  'aicocktails' 
password = 'Recipes2019' 
tablename = 'result'

@app.route('/', methods=['GET','POST'])
def entry_page():
    try:
        if request.form['gohome']:
            return render_template('index.html')
    except:
        return render_template('index.html')
  
@app.route('/generate_recipe/', methods=['GET', 'POST'])
def predict():
    try:
        global alcohol_choice, season_choice, music_choice, flavor_choice
        # get form answers to the four questions
        alcohol_choice = request.form['alcohol']
        season_choice = request.form['season']
        music_choice = request.form['music']
        flavor_choice = request.form['flavor']
        answers = alcohol_choice + ' ' + season_choice + ' ' + music_choice + ' ' + flavor_choice
                    
    except:
        message = "Please answer all the questions!"
        return render_template('index.html',
                               message=message)
    
    # call your message functions here
    global message0, message1, message2, message3, message4
    message0 = return_answers(answers)
    message1 = generate_drink_output(answers, model, graph) 
    message2 = vikram_generate_drink_output(answers, model2, graph2)
    message3 = generate_textgenrnn_drink(answers, model3, graph3)
    message4 = (generate_textgenrnn_drink(answers, model4, graph4)).lower()
   
    return render_template('answers.html', 
                           message0=message0, 
                           message1=message1,
                           message2=message2, 
                           message3=message3, 
                           message4=message4)

@app.route('/recipe_complete/', methods=['GET', 'POST'])
def sendtodb():
    html = """
    <a href="/">
        <img src="https://www.avanade.com/en/solutions/cloud-and-application-services/~/media/logo/share-avanade-logo.jpg" alt="Avanade"  height="80" >
    </a>
    <br>
    <div style="color: #ff8138; font-size: 28px; padding-top: 15px; text-align: center; font-family: Arial; font-weight: bold;"> 
    Thank you for using our AI Cocktail Maker! </div>
    <br>
    <center>
    <a href="/">
      <button style="position: center; padding: 10px 10px 10px 10px !important; font-size: 16px !important; 
      background-color: #ff8138; font-weight: bold; color: white; border-radius: 5px;" type="submit" value="Submit" class="btn btn-primary" name="submit">
          🍹 Another Round 🍹
      </button>
    </a>
    </center>
    """
    return html

    recipe_choice = request.form['recipe']
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = cnxn.cursor()
    # Need to parse answer to be separate ingredients again, then insert into
    # Liquor, Ing1-8, and then drink_id = which model it was
    recipe_choice_int = (ord(recipe_choice) - 97) # the number version of the recipe chosen
    recipe_string = [message1, message2, message3, message4][recipe_choice_int] # the recipe string chosen
    recipe_list = recipe_string.split(',') # convert the string to a list
    recipe_list = [c.strip() for c in recipe_list] # clean the strings
    liquor = recipe_list.pop(0) # the first ingredient is the main liquor
    if len(recipe_list) < 8: # ensure the final ingredients list is of length 8 to properly fill in the SQL database
        empty_strings = (8-len(recipe_list))*[''] # add empty strings to pad the end of the ingredients list
        ingredients_list = recipe_list + empty_strings
    # insert the values above into the SQL database
    cursor.execute('''
                INSERT INTO dbo.result (Question1, Question2, Question3, Question4, Answer, Liquor, Ingredient1, Ingredient2, Ingredient3,Ingredient4,Ingredient5,Ingredient6,Ingredient7,Ingredient8)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                alcohol_choice, season_choice, music_choice, flavor_choice, recipe_choice, liquor, ingredients_list[0], ingredients_list[1], ingredients_list[2], ingredients_list[3], ingredients_list[4], ingredients_list[5], ingredients_list[6], ingredients_list[7])
    cnxn.commit()
    message = "Thank you for using the AI Cocktail Maker!"
    submission_successful = True
    return render_template('answers.html',
                               message=message,
                               submission_successful=submission_successful,
                               message0=message0,
                               message1=message1,
                               message2=message2,
                               message3=message3,
                               message4=message4)

        
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    #app.run(debug=True)