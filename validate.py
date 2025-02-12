import argparse
import methods
import imp
imp.reload(methods)
import tensorflow as tf
import pickle as pk
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import os
import numpy as np
from scoring import *
from model.models import SplitTS
from tensorflow.python.framework.ops import disable_eager_execution

def validate(validation_function):
    feature_faker_list = {
        'mean': lambda _min, _max, _mean, _std, _size: np.random.normal(_mean, _std, _size),
        'normal_noise': lambda _min, _max, _mean, _std, _size: np.random.normal(_mean, _std, _size),
        'uniform_noise': lambda _min, _max, _mean, _std, _size: np.random.uniform(_min, _max, _size),
        'zero': lambda _min, _max, _mean, _std, _size: 0,
        'one': lambda _min, _max, _mean, _std, _size: 1,   
    }

    results = []
    
    # Kernel SHAP
    print("Kernel SHAP")
    for ff_name, feature_faker in feature_faker_list.items():

        explainer = methods.KernelSHAP(model, nsamples=1000, nsegments=5, 
                               feature_faker=feature_faker)

        score = validation_function(model, explainer)
        results.append({'method': 'Kernel SHAP', 'feature faker': ff_name, 
                        'score': score})
    
    # GRAD CAM
    # Will be computed with gradcam_search.py
    '''
    print("GRAD CAM")
    layers = [l.name for l in model.layers if 'conv2d' in l.name]
    for last_conv_layer_name in layers:
        for feature_dimension in [True, False]:
            for time_dimension in [True, False]:
                #last_conv_layer_name = f"conv2d_{layer}"
                explainer = methods.GRADCAM(model, last_conv_layer_name, 
                                                    feature_dimension=feature_dimension,
                                                    time_dimension=time_dimension)

                score = validation_function(model, explainer)

                results.append({'method': 'GRADCAM', 
                                'time_dimension': time_dimension,
                                'feature_dimension': feature_dimension,
                                'layer': last_conv_layer_name, 
                                'score': score})
    '''
    
    # Lawer Wise Relevance Propagation (LRP)
    print("LRP")
    for mode  in ['source', 'none']:

        explainer = methods.LRP(model, mode=mode)

        score =  validation_function(model, explainer)
        results.append({'method': 'LRP', 'mode': mode, 
                        'score': score})  
    
    print("Saliency")
    explainer = methods.Saliency(model)

    score = validation_function(model, explainer)
    results.append({'method': 'Saliency', 
                    'score': score})  
   
    # Lime
    print("Lime")
    for ff_name, feature_faker in feature_faker_list.items():

        explainer = methods.Lime(model, nsamples=1000, nsegments=5, 
                               feature_faker=feature_faker)

        score =  validation_function(model, explainer)
        results.append({'method': 'Lime', 
                        'feature faker': ff_name, 
                        'score': score})    
        
  


 
        
    # Lawer Wise Relevance Propagation (LRP)
    print("LRP")
    for mode  in ['source', 'none']:

        explainer = methods.LRP(model, mode=mode)

        score =  validation_function(model, explainer)
        results.append({'method': 'LRP', 'mode': mode, 
                        'score': score})    




    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    
    # Adding optional argument
    parser.add_argument("-d", "--Device", help = "CUDA DEVICE")
    parser.add_argument("-p", "--Proxy", help = "{identity, stability, }", required=True)
    parser.add_argument("-m", "--Model", help = "Model directory", required=True)

    # Read arguments from command line
    args = parser.parse_args()
    
    if args.Device:
        os.environ["CUDA_VISIBLE_DEVICES"]=args.Device
    
    if not os.path.exists(os.path.join(args.Model, 'results')):
        os.makedirs(os.path.join(args.Model, 'results'))
    
    
    samples2 = pk.load(open(os.path.join(args.Model, 'samples.pk'), 'rb')).astype(np.float32)
    targets2 = pk.load(open(os.path.join(args.Model, 'targets.pk'), 'rb')).astype(np.float32)
    print("Samples readed")
    
    
    model = tf.keras.models.load_model(os.path.join(args.Model, 'model.h5'), 
                                   custom_objects={'LeakyReLU': tf.keras.layers.LeakyReLU,
                                                  'NASAScore': NASAScore,
                                                  'SplitTS': SplitTS,
                                                  'PHM21Score': PHM21Score})
    print("Model readed")
    

    if args.Proxy == 'identity':
        validation_function = lambda model, explainer: methods.validate_identity(model, explainer, samples2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/identity.pk'), 'wb'))
        
    elif args.Proxy == 'selectivity':
        validation_function = lambda model, explainer: methods.validate_selectivity(model, explainer, samples2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/selectivity.pk'), 'wb'))

    elif args.Proxy == 'stability':
        validation_function = lambda model, explainer: methods.validate_stability(model, explainer, samples2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/stability.pk'), 'wb'))
        
    elif args.Proxy == 'separability':
        validation_function = lambda model, explainer: methods.validate_separability(model, explainer, samples2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/separability.pk'), 'wb'))
        
    elif args.Proxy == 'cs':
        validation_function = lambda model, explainer: methods.validate_coherence(model, explainer, samples2, targets2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/cs.pk'), 'wb'))   
        
    elif args.Proxy == 'acumen':
        validation_function = lambda model, explainer: methods.validate_acumen(explainer, samples2)
        results = validate(validation_function)
        pk.dump(results, open(os.path.join(args.Model, 'results/acumen.pk'), 'wb'))           
