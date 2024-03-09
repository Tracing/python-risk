from ai_helper import get_data
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
import sklearn as sk
import sklearn.metrics as skme
import sklearn.model_selection as skm
import sklearn.linear_model as skl
import sklearn.neural_network as sknn

def test_model(name, model, data):
    (xs_train, xs_test, ys_train, ys_test) = data
            
    xs_train = np.concatenate((xs_train, xs_train ** 2), axis=1)
    xs_test = np.concatenate((xs_test, xs_test ** 2), axis=1)
    
    model.fit(xs_train, ys_train)
    
    ys_pred = model.predict(xs_train)
    r2_score = skme.r2_score(ys_train, ys_pred)
    
    print("Model {} got an r2 score of {:.4f} on the train set.".format(name, r2_score))
    
    ys_pred = model.predict(xs_test)
    r2_score = skme.r2_score(ys_test, ys_pred)
    
    print("Model {} got an r2 score of {:.4f} on the test set.".format(name, r2_score))

def test_coefficients(weights, data):
    (xs_train, xs_test, ys_train, ys_test) = data
    xs_test = np.concatenate((xs_test, xs_test ** 2), axis=1)
    ys_pred = np.matmul(xs_test, weights)
    
    r2_score = skme.r2_score(ys_test, ys_pred)
    print("r2 score of {:.4f} on the train set.".format(r2_score))
    
def test_armies_heuristic(data):
    (_, xs_test, _, ys_test) = data
    ys_pred = []
    for i in range(xs_test.shape[0]):
        total_armies = np.sum(xs_test[i, 0:42])
        n_player_armies = np.sum(xs_test[i, 0:42] * xs_test[i, 42:84])
        if total_armies == 0:
            ys_pred.append(0.5)
        else:
            ys_pred.append(n_player_armies / total_armies)
    
    r2_score = skme.r2_score(ys_test, ys_pred)
    print("Armies heuristic got an r2 score of {:.4f} on the test set.".format(r2_score))

if __name__ == "__main__":
    states = "states.npy"
    results = "results.npy"
    outfile = "coefficiencts.npy"
    
    #(399591, 87)
    #(399591,)
    #Model Linear got an r2 score of 0.4812 on the test set.
    #Armies heuristic got an r2 score of 0.4055 on the test set.
    #Model Neural Network 100 got an r2 score of 0.8217 on the test set.
    #Model Neural Network 150 got an r2 score of 0.8664 on the test set.
    #Model Neural Network 200 got an r2 score of 0.8785 on the test set.
    #Model Neural Network 250 got an r2 score of 0.8903 on the test set.
    #Model Neural Network 300 got an r2 score of 0.9049 on the test set.
    #Model Neural Network (300, 300) got an r2 score of 0.9691 on the test set.
    #Model Neural Network (300, 300, 150) got an r2 score of 0.9771 on the test set.
    
    data = get_data(states, results)
    
    linear = skl.LinearRegression()
    test_model("Linear", linear, data)
    np.save(outfile, linear.coef_)
    
    test_coefficients(np.load(outfile), data)

        
    
    #for n in [(300, 300, 150)]:
    #    test_model("Neural Network {}".format(n), sknn.MLPRegressor(hidden_layer_sizes=n), data)
    #test_armies_heuristic(data)