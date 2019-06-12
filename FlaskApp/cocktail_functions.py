# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:57:37 2019

@author: v-cabad
"""
import flask
import pandas as pd
import numpy as np
import math
import re
import itertools
import pickle
import random
import collections
import sklearn
import keras
import tensorflow as tf
from keras.preprocessing.text import text_to_word_sequence
from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras import backend as K
import keras.utils as ku 
from keras.layers import Dropout
from keras.layers import Bidirectional
from keras.models import load_model, model_from_json
from textgenrnn import textgenrnn
from collections import OrderedDict
import random



with open('models/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

with open('models/vik_tokenizer.pickle', 'rb') as handle2:
    tokenizer2 = pickle.load(handle2)

# Generates potential ingredient list based on answers to the four questions (seed text)
def generate_text(seed_text, next_words, max_sequence_len, model,graph):
    x = set()
    drink_list = []
    for j in range(next_words):
        # convert input into vectorized format
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        # prepare vector for input into model
        token_list = pad_sequences([token_list], maxlen= 
                             max_sequence_len-1, padding='pre')
        # make a prediction for what word could come after the input sequence
        with graph.as_default():
            #y_hat = keras_model_loaded.predict(predict_request, batch_size=1, verbose=1)
            predicted = model.predict_classes(token_list) #, verbose=0)
  
        output_word = ""
        # find the corresponding word to the vectorized output
        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        # new seed_text is the predicted word + space
        seed_text += " " + output_word
        # if the output_word is unique from the growing list
        # add it to the set of predicted words
        # otherwise go to the next prediction
        if(output_word not in x):
            drink_list.append(output_word)
            x.add(output_word)
    return drink_list


def vikram_generate_text(seed_text, next_words, max_sequence_len, loaded_model, graph):
    print(seed_text)
    x = set()
    drink_list = []
    for j in range(next_words):
        token_list = tokenizer2.texts_to_sequences([seed_text])[0]
        print(tokenizer2.texts_to_sequences([seed_text]))
        token_list = pad_sequences([token_list], maxlen=
        max_sequence_len - 1, padding='pre')
        with graph.as_default():
            predicted = loaded_model.predict_classes(token_list, verbose=0)
        output_word = ""
        for word, index in tokenizer2.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += " " + output_word
        if (output_word not in x):
            if (output_word != 'any'):
                drink_list.append(output_word)
            x.add(output_word)
    return drink_list


def vikram_generate_drink_output(txt_input_2, model, graph):
    list_input_2 = vikram_generate_text(txt_input_2, 15, 13, model, graph)
    liquor = list_input_2.pop(0)
    ingredients = [7,5,4,4]
    final_drink = [liquor]
    item = ord(txt_input_2.split()[2]) - 96
    for count in range (0,ingredients[item-1]):
        a = random.choice(list_input_2)
        if a in final_drink:
            count = count - 1
        else:
            final_drink.append(a)
    for a in range(0,len(final_drink)):
        final_drink[a] = final_drink[a].replace('-', ' ').strip()
    final_drink = ', '.join(final_drink)
    return final_drink

def generate_drink_output(four_questions, model, graph):
    ingredient_list = generate_text(four_questions, 15, 13, model, graph)
    # print(ingredient_list)
    liquor = ingredient_list.pop(0) # extract liquor from list of ingredients
    ingredients = [3,4,5,7] # number of ingredients associated with each response to music question
    num_ing_indicator = ord(four_questions.split()[2]) - 96 # getting the number of ingredients based on music choice?
    num_ing = ingredients[num_ing_indicator-1] # number of ingredients
#     select_ingredients = random.choices(ingredient_list,k=num_ing) # randomly select number from ingredient list
    select_ingredients = list(np.random.choice(ingredient_list, size=num_ing, replace=False)) #
    final_drink = [liquor] + select_ingredients # final drink is the liquor plus the ingredients
    final_drink = [ing.replace('-',' ').strip() for ing in final_drink] # remove the dashes
    # print("Here's your Drink:")
    final_drink = ', '.join(final_drink)

    return final_drink


#drink chosen by generating 10 recipes, cleaning them up, filtering out recipes with less than 3 ingredients then randomly selecting from that list
def generate_textgenrnn_drink(answers, model, graph):
    answers = answers.replace(' ', ',')
    # make a prediction for what word could come after the input sequence
    with graph.as_default():
        #y_hat = keras_model_loaded.predict(predict_request, batch_size=1, verbose=1)
        generated_drinks = model.generate(1, return_as_list=True, prefix=answers, temperature=.6, top_n=20)
        
    drink_list = []
    for drink in generated_drinks:
        drink = drink[8:]
        drink = drink.split(',')
        drink = [ingredient for ingredient in drink if ingredient != '']
        ingredient_list = list(OrderedDict.fromkeys(drink))
        drink_list.append(ingredient_list)

    final_drink = ','.join(drink_list[0])


    return final_drink

    

def return_answers(answers):
    answers_list = [ord(x)-97 for x in answers.split()]
    answers_dict = {0: ['Whiskey', 'Vodka', 'Tequila','Rum'],
                1:  ['Fall', 'Winter', 'Spring','Summer'],
                2: ['Some Sinatra', 'Probably Rock', 'Big Chart-Toppers','Hot Club Hits'],
                3: ['Frozen', 'Fruity', 'Hot', 'Sour','Sweet','Floral']}
    answer_words = []
    for i in range(4):
        selection = answers_list[i]
        answer_words.append(answers_dict[i][selection])
    return ', '.join(answer_words)