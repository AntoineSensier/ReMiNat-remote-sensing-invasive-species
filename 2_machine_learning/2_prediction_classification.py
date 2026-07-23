# -*- coding: utf-8 -*-
"""
Script for prediction of classification with a previously trained model
Require data for prediction from image processing and model
Inputs:
    - training data (to get the classes to predict)
    - training model
    - data to be predicted (one file or a folder with files, files are vector polygons)
Outputs:
    - result of classification model on data to be predicted
Author : Antoine Sensier, CIRAD, 2026

"""
from functions_machine_learning import *

# Inputs
path_root = 'D:/Data' # to be changed

path_data_sample = path_root+'/sample/sample_zonal_stat.gpkg' # to be changed

path_model = path_root+'/models1/model_rf_v1.pkl' # to be changed
# path_scale = path_root+'/models/model_rf_norm_scale.pkl'

# Outputs
output_name_classification = "_classif_rf"

path_data_to_predict = path_root+'/zonal_stat/list' # a file or a folder, to be changed

path_output = path_root+'/results/list1'
os.makedirs(path_output, exist_ok=True)
layer_merged = 'test_cl_merged.gpkg'
path_output_final = path_root+'/results/'+layer_merged

#  prediction based on the model
model = pickle.load(open(path_model, 'rb'))

# useful for retrieving the labels associated with the classes
data_input = gpd.read_file(path_data_sample)

data_input = data_input.drop(columns=['fid'], errors='ignore')

labels = data_input.drop_duplicates(subset=['classvalue']).set_index('classvalue')['classname'].to_dict()
labels = dict(sorted(labels.items())) # to sort the classes by value


if os.path.isdir(path_data_to_predict): # if we browse a directory
    path_data_to_predict = [path_data_to_predict+'/'+f for f in os.listdir(path_data_to_predict) if f.endswith('.gpkg')] #'.shp'
else:
    path_data_to_predict = [path_data_to_predict]

for file_data_to_predict in path_data_to_predict:
    # Importing data to be predicted
    try:
        data_to_predict = gpd.read_file(file_data_to_predict)
        data_to_predict = data_to_predict.dropna()  # Remove rows if a field has a NaN value

        if len(data_to_predict)>0:
            selected_features = model.feature_names_in_.tolist()
            print(file_data_to_predict)
            print(len(selected_features))
            print(selected_features)

            geometry = data_to_predict['geometry']
            data_pred = data_to_predict[selected_features]

            # # for standardization
            # sc = pickle.load(open(path_scale, 'rb'))
            # sc.fit(data_pred)
            # data_pred = scaling_data(sc, data_pred)

            # Direct prediction: selects the class with the highest probability
            ypred = model.predict(data_pred)

            # Obtain the probabilities for each class
            yproba = model.predict_proba(data_pred)
            # yproba = None

            # write_result_classification_proba_class(data_pred, geometry, ypred, yproba, labels, path_output, file_data_to_predict, output_name_classification,model)
            write_result_classification(data_pred, geometry, ypred, yproba, labels, path_output, file_data_to_predict, output_name_classification, None)
    except Exception as e:
        print(f"Erreur avec {file_data_to_predict}")

# Merge gpkg files of the output folder in one file
# Loop over all GPKG files
gpkg_files = [os.path.join(path_output, f) for f in os.listdir(path_output) if f.endswith(".gpkg")]
# Save to a new GPKG file
first_write = True
for file in gpkg_files:
    if output_name_classification in file:
        try:
            layers = fiona.listlayers(file)
            for layer in layers:
                print(f"Reading {file} (layer: {layer})")
                gdf = gpd.read_file(file, layer=layer)

                # Si le GeoDataFrame est vide, on ignore
                if gdf.empty:
                    continue

                # Write (mode 'w' once, then 'a')
                gdf.to_file(path_output_final, layer=layer_merged, driver="GPKG", mode="w" if first_write else "a")
                first_write = False
            os.remove(file)
        except Exception as e:
            print(f"Erreur avec {file} : {e}")