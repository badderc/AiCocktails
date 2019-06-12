from keras.models import model_from_json
import tensorflow as tf


def init_model(json_file,weight):
    json_file = open(json_file, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    # compile model
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(weight)
    print("loaded model from disk")
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam')
    graph = tf.get_default_graph()
    
    return loaded_model, graph

