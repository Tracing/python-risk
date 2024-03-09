from agent import BaseAgent, play_n_games_seq
from ai_helper import get_data, get_state_2
from data_gathering import gather_data
import sklearn.metrics as skme
import numpy as np
import tensorflow as tf

def get_linear_model(weights_path=None):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input((None, 96)))
    model.add(tf.keras.layers.Dense(1, activation="linear"))
    
    if not weights_path is None:
        model(tf.zeros((1, 96)))
        model.load_weights(weights_path)
        
    return model

def get_small_model(weights_path=None):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input((None, 96)))
    model.add(tf.keras.layers.Dense(64, activation=tf.keras.layers.LeakyReLU(0.3)))
    model.add(tf.keras.layers.Dense(1, activation="linear"))
    
    if not weights_path is None:
        model(tf.zeros((1, 96)))
        model.load_weights(weights_path)
        
    return model

def get_model(weights_path=None):
    #0.40518145481598633
    #2.0088
    n = 75
    
    inputs = tf.keras.Input(shape=(None, 96))
    x = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(inputs)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x1)
    x = tf.keras.layers.Add()([x, x1])
    
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x1)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x1)
    x = tf.keras.layers.Add()([x, x1])
    
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x1)
    x1 = tf.keras.layers.Dense(n, activation=tf.keras.layers.LeakyReLU(0.3))(x1)
    x = tf.keras.layers.Add()([x, x1])

    outputs = tf.keras.layers.Dense(1, activation="linear")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
    if not weights_path is None:
        model(tf.zeros((1, 96)))
        model.load_weights(weights_path)
        
    return model

def train(model: tf.keras.Sequential, data, weights_outfile="heuristic_weights.h5"):
    #0.38827421291762143
    (xs_train, xs_test, ys_train, ys_test) = data
    
    model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=weights_outfile,
    monitor='val_mse',
    mode='min',
    save_best_only=True,
    save_weights_only=True,
    verbose=1)
    
    optimizer = tf.keras.optimizers.Adam()
    model.compile(optimizer=optimizer, loss="mse", metrics=["mse"])
    model.fit(xs_train, ys_train, batch_size=256, epochs=50, validation_split=0.25, verbose=1, shuffle=True, 
              callbacks=[model_checkpoint_callback])

    model.load_weights(weights_outfile)    
    print(model.evaluate(xs_test, ys_test, batch_size=256))
    
    ys_pred = model.predict(xs_test, batch_size=256)
    print(skme.r2_score(ys_test, ys_pred))
    

class NeuralAgent(BaseAgent):
    def __init__(self, weights_path):
        super().__init__()
        self.model = get_model(weights_path)
        
    def get_action(self):
        if self.game.get_state() == 'setup':
            return super().get_action()
        else:
            actions = self.get_actions()
            best_action = None
            states = []
            
            for action in actions:
                game = self.game.copy(True)
                self.do_actions_to_game(action, game)
                if game.has_finished() and game.get_winner() == self.game.get_player_turn():
                    return action
                states.append(get_state_2(game))
                
            states = tf.concat(states, 0)
            scores = self.model(states, training=False)
    
            best_action = actions[tf.argmax(scores, 0)[0]]
            
            return best_action
    
if __name__ == "__main__":
    #gather_data(40000, "states.npy", "results.npy", 5)
    
    states = "states.npy"
    results = "results.npy"
    
    #linear
    #0.3285658803763962 - adam, 0.3392 - optimal - needs more epochs
    #Score is 0.0600+-0.0294 with 250 games
    
    #small
    #0.37734621041511807 - needs test with more epochs and best loss saving
    #Score is 0.2080+-0.0503 with 250 games
    
    #big
    #0.4060620394153609 - needs test with more epochs and best loss saving
    #Score is 0.4300+-0.0970 with 100 games
    
    model = get_model()
    data = get_data(states, results)
    train(model, data)
    
    n_games = 100
    (score, deviation) = play_n_games_seq(n_games, NeuralAgent("heuristic_weights.h5"))
    print("Score is {:.4f}+-{:.4f} with {} games".format(score, deviation, n_games))