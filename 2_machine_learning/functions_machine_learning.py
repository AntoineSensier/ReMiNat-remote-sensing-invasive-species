# -*- coding: utf-8 -*-
"""
List of functions used in 1_train_classification and 2_prediction_classification scripts


Author : Antoine Sensier, CIRAD, 2026

"""
import geopandas as gpd
from scipy.stats import entropy
import pandas as pd
import numpy as np
import networkx as nx
from sklearn.metrics import silhouette_samples
import joblib
from xgboost import XGBClassifier
import os
from tqdm import tqdm
from lightgbm import LGBMClassifier
import fiona
import random
from sklearn.base import clone, BaseEstimator, ClassifierMixin
import networkx as nx
from collections import Counter
from itertools import combinations
from copy import deepcopy
import mlxtend
import pickle
from sklearn.utils import shuffle
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import AgglomerativeClustering
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.feature_selection import VarianceThreshold, mutual_info_classif
from sklearn.tree import DecisionTreeClassifier, export_text, export_graphviz
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC, SVC, SVR
from sklearn.ensemble import VotingClassifier
from sklearn.datasets import make_regression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score,cross_validate, GridSearchCV,RandomizedSearchCV
from sklearn.feature_selection import SelectFromModel, RFE, RFECV, SequentialFeatureSelector
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score, make_scorer, accuracy_score, \
    roc_curve, auc, ConfusionMatrixDisplay, pairwise_distances, precision_score
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold,KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import silhouette_score
from mlxtend.classifier import OneRClassifier
from matplotlib import pyplot
from sklearn.tree import plot_tree
from sklearn.base import BaseEstimator, TransformerMixin

# Set a seed for reproducibility
random.seed(0)

def calculate_tss(conf_matrix):
    num_classes = conf_matrix.shape[0]
    TSS_values = []

    for i in range(num_classes):
        TP = conf_matrix[i, i]
        FN = np.sum(conf_matrix[i, :]) - TP
        FP = np.sum(conf_matrix[:, i]) - TP
        TN = np.sum(conf_matrix) - (TP + FN + FP)

        if TP + FN == 0 or FP + TN == 0:
            TSS = np.nan
        else:
            TSS = (TP / (TP + FN)) - (FP / (FP + TN))

        TSS_values.append(TSS)

    TSS_global = np.nanmean(TSS_values)
    TSS_values = np.array(TSS_values, dtype=np.float64)
    return TSS_global, TSS_values.tolist()

def tss_score(y_true, y_pred):
    labels = np.unique(y_true)
    tss_list = []
    for c in labels:
        y_true_bin = (y_true == c).astype(int)
        y_pred_bin = (y_pred == c).astype(int)
        cm = confusion_matrix(y_true_bin, y_pred_bin)
        if cm.shape != (2, 2):
            continue  # ignore si pas de positif dans y_true
        tn, fp, fn, tp = cm.ravel()
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        tss = sens + spec - 1
        tss_list.append(tss)
    return np.mean(tss_list)
def calculate_overall_accuracy(conf_matrix):
    TP_total = np.trace(conf_matrix)
    total = np.sum(conf_matrix)
    overall_accuracy = TP_total / total
    return overall_accuracy

def calculate_kappa(conf_matrix):
    total = np.sum(conf_matrix)
    TP_total = np.trace(conf_matrix)
    overall_accuracy = TP_total / total
    total_lignes = np.sum(conf_matrix, axis=1)
    total_colonnes = np.sum(conf_matrix, axis=0)
    Pe = np.sum(total_lignes * total_colonnes) / (total * total)

    kappa = (overall_accuracy - Pe) / (1 - Pe)
    return kappa

# Precision (P) is the proportion of true positive (TP) samples over the whole
# number of positive samples, true and false (FP): P = TP / (TP + FP)
def calculare_precision(conf_matrix):
    num_classes = conf_matrix.shape[0]
    P_values = []

    for i in range(num_classes):
        TP = conf_matrix[i, i]
        FP = np.sum(conf_matrix[:, i]) - TP
        if (TP + FP) == 0:
            P = 1
        else:
            P = TP / (TP + FP)
        P_values.append(P)

    P_global = np.nanmean(P_values)
    return P_global, P_values

# Recall (R) is the proportion of true positive samples over the whole number of
# true samples:  R = TP / (TP + FN)
def calculare_recall(conf_matrix):
    num_classes = conf_matrix.shape[0]
    R_values = []

    for i in range(num_classes):
        TP = conf_matrix[i, i]
        FN = np.sum(conf_matrix[i, :]) - TP
        R = TP / (TP + FN)
        R_values.append(R)

    R_global = np.nanmean(R_values)
    return R_global, R_values

def calculare_fscore(conf_matrix):
    num_classes = conf_matrix.shape[0]
    fscore_values = []

    for i in range(num_classes):
        TP = conf_matrix[i, i]
        FN = np.sum(conf_matrix[i, :]) - TP
        FP = np.sum(conf_matrix[:, i]) - TP
        fscore = (2*TP) / (2*TP+FP+FN)
        fscore_values.append(fscore)

    fscore_global = np.nanmean(fscore_values)
    return fscore_global, fscore_values

# Score calculations and a confusion matrix (optional)
def assessment_model(classes_validation, prediction,labels, write_matrix, path_conf_matrix):
    # Evalution (accuracy, recall, F-score, TSS)
    conf_matrix = confusion_matrix(classes_validation, prediction, labels = list(labels.keys()))
    TSS_global, TSS_values = calculate_tss(conf_matrix)
    kappa = calculate_kappa(conf_matrix)
    overall_accuracy = calculate_overall_accuracy(conf_matrix)
    accuracy_per_class = conf_matrix.diagonal() / conf_matrix.sum(axis=1)
    P_global, P_values = calculare_precision(conf_matrix)
    R_global, R_values = calculare_recall(conf_matrix)
    FS_global, FS_values = calculare_fscore(conf_matrix)

    TSS_global = round(TSS_global, 3)
    kappa = round(kappa, 3)
    overall_accuracy = round(overall_accuracy, 3)
    P_global = round(P_global, 3)
    R_global = round(R_global, 3)
    FS_global = round(FS_global, 3)

    print(f"TSS global : {TSS_global}")
    print(f"Kappa : {kappa}")
    print(f"Overall Accuracy : {overall_accuracy}")
    print(f"Precision global : {P_global}")
    print(f"Recall global : {R_global}")
    print(f"F-score global : {FS_global}")

    list_index = ["TSS", "Accuracy", "Precision", "Recall", "F-score"]
    list_scores_classes = [TSS_values, accuracy_per_class, P_values, R_values, FS_values]
    array_scores = pd.DataFrame(list_scores_classes, columns=list(labels.values()), index=list_index)
    array_scores = np.round(array_scores.astype(float), 3)
    print(array_scores.to_string())
    html_table = array_scores.to_html()
    # Sauvegarder le fichier HTML
    with open('D:/array_scores.html', 'w') as f:
        f.write(html_table)

    if write_matrix:
        unique_classes = sorted(set(classes_validation) | set(prediction))
        conf_matrix_csv = pd.DataFrame(conf_matrix, index=list(labels.keys()), columns=list(labels.keys()))
        conf_matrix_csv.to_csv(path_conf_matrix, header=False, index=False)


    disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=labels.values())
    # conf_matrix_normalized = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis]
    # disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_normalized, display_labels=labels.values())
    disp.plot()
    pyplot.xticks(rotation=45, ha='right', fontsize=7)
    pyplot.yticks(fontsize=7)
    pyplot.show()
    # return overall_accuracy, kappa, TSS_global, TSS_values
    return {
        "TSS_global": TSS_global,
        "Kappa": kappa,
        "OA": overall_accuracy,
        "Precision_global": P_global,
        "Recall_global": R_global,
        "Fscore_global": FS_global,
        "TSS": TSS_values,
        "Accuracy": accuracy_per_class,
        "Precision": P_values,
        "Recall": R_values,
        "Fscore": FS_values
    }


# Standardizes the features
def scaling_data(scaling, data_train):
    # Scaling the data
    # data_colums = data_train.columns
    scaled_data = scaling.transform(data_train)
    data_train = pd.DataFrame(scaled_data, columns=data_train.columns, index=data_train.index)
    # data_train.columns = data_colums
    return data_train

# Removal of strongly correlated features (Pearson correlation)
def remove_correlated_features(X, threshold):
    correlation_matrix = X.corr().abs()
    # Selectionner la partie supérieure de la matrice de corrélation
    upper = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
    # Trouver les features ayant une corrélation supérieure à un seuil
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    print(f'Redundant features (correlation > {threshold}): {to_drop}')
    print(f'Removed features :  {len(to_drop)}')
    df_reduced = X.drop(columns=to_drop)
    return df_reduced

# Calculate feature importance and retain features based on a threshold.
def selection_features_from_model(classifier, X_train, y_train, threshold):
    classifier.fit(X_train, y_train)
    selector = SelectFromModel(classifier, prefit=True, threshold=threshold)
    selected_features_mask = selector.get_support()
    selected_features = X_train.columns[selected_features_mask].tolist()
    return selected_features

def result_permutation_importance_features(list_result_mean_full, list_result_mean_std, name_features):
    result_mean_full_ = pd.DataFrame(np.vstack(list_result_mean_full))
    result_mean_std_ = pd.DataFrame(np.vstack(list_result_mean_std))
    mean_of_result_mean_full = result_mean_full_.mean()
    mean_of_result_std_full = result_mean_std_.mean()
    mean_of_result_full = pd.concat([mean_of_result_mean_full, mean_of_result_std_full], axis=1)
    mean_of_result_full.columns = ["mean", "std"]
    mean_of_result_full.index = name_features
    forest_importances_mean = pd.Series(mean_of_result_full["mean"], index=mean_of_result_full.index)
    forest_importances_std = pd.Series(mean_of_result_full["std"], index=mean_of_result_full.index)
    result2 = pd.concat([forest_importances_mean, forest_importances_std], axis=1)
    result2.columns = ["mean", "std"]
    result2 = result2.sort_values('mean')
    res_mean = result2["mean"]
    res_std = result2["std"]
    res_val_sup0 = res_mean[res_mean > 0]

    # print("list of all features")
    res_val_sup0e = res_mean[res_mean <= 0]
    print(res_mean.index)
    print("list of relevant features (>0)")
    print(res_val_sup0.index)
    fig, ax = pyplot.subplots()
    res_mean.plot.bar(res_std, ax=ax)
    ax.set_title("Feature importances using permutation")
    ax.set_ylabel("Mean accuracy decrease")
    fig.tight_layout()
    pyplot.show()

    return res_val_sup0

# Feature selection via permutation importance
def selection_features_permutation_importance(data_train, classes_train, data_validation, classes_validation, nb_iteration, random_state):
    # Generate a list of 100 random values ​​between 0 and 1000
    list_random_param = random.sample(range(0, 1000), nb_iteration)
    if random_state not in list_random_param:
        list_random_param[nb_iteration-1] = random_state
    result_mean_full = []
    result_mean_std = []
    i=0
    for random_val in list_random_param:
        print(f"Permutation repeat {i + 1}/{nb_iteration}")
        print(f"Random Value :{random_val}")
        # Initialize the classifier
        classifier = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=random_val, n_jobs=-1)
        # Fit the model to the training data
        classifier.fit(data_train, classes_train)
        # Predict classes on the validation set
        # prediction = classifier.predict(data_validation)
        # Evaluate the model
        result = permutation_importance(classifier, data_validation, classes_validation, n_repeats=5, random_state=random_state, n_jobs=-1)
        result_mean_full.append(result.importances_mean)
        result_mean_std.append(result.importances_std)
        i+=1

    # Selection of the most important features
    imp_features = result_permutation_importance_features(result_mean_full, result_mean_std, data_validation.columns)
    selected_features = imp_features.index.tolist()
    return selected_features

# Selection of features with inner CV
def selection_features_permutation_CV_robust(
        data, classes, cv,
        nb_repeats_cv=25,  # Repeat  CV 25 times
        nb_repeats_perm=5,  # Internal permutation repetitions
        random_state=0
):
    all_importances = []
    total_iterations = nb_repeats_cv * cv.n_splits
    current_iter = 0

    for repeat in range(nb_repeats_cv):
        # new stratification at each repetition
        cv_iter = StratifiedKFold(
            n_splits=cv.n_splits,
            shuffle=True,
            random_state=random_state + repeat
        )

        for fold_idx, (train_idx, val_idx) in enumerate(cv_iter.split(data, classes)):
            current_iter += 1
            print(f"Iteration {current_iter}/{total_iterations} (repeat {repeat + 1}, fold {fold_idx + 1})")

            X_train = data.iloc[train_idx]
            y_train = classes.iloc[train_idx]
            X_val = data.iloc[val_idx]
            y_val = classes.iloc[val_idx]

            # Train RF
            rf = RandomForestClassifier(
                n_estimators=100,
                class_weight="balanced",
                random_state=random_state,
                n_jobs=-1
            )
            rf.fit(X_train, y_train)

            # Permutation importance
            perm = permutation_importance(
                rf, X_val, y_val,
                n_repeats=nb_repeats_perm,
                random_state=random_state + repeat,
                n_jobs=-1
            )

            all_importances.append(perm.importances_mean)

    # Average across all iterations
    importances_mean = np.mean(all_importances, axis=0)
    importances_std = np.std(all_importances, axis=0)

    df = pd.DataFrame({
        "mean": importances_mean,
        "std": importances_std
    }, index=data.columns)

    selected = df[df["mean"] > 0].sort_values("mean", ascending=False)

    # Visualisation
    selected["mean"].plot.bar(yerr=selected["std"])
    pyplot.title(f"Permutation Importance (CV répétée {nb_repeats_cv}x)")
    pyplot.tight_layout()
    pyplot.show()

    return selected.index.tolist()

# Selection of features with premutation importance with random value for split train and RF parameter
def selection_features_permutation_importance_with_random_train(data_input, classes, nb_iteration, random_state, index_target=0):
    list_tss = []
    list_tss_exo = []
    # Generate a list of 100 random values between 0 and 1000
    list_random_param1 = random.sample(range(0, 1000), nb_iteration)
    list_random_param2 = random.sample(range(0, 1000), nb_iteration)
    if random_state not in list_random_param1:
        list_random_param1[nb_iteration-1] = random_state
    if random_state not in list_random_param2:
        list_random_param2[nb_iteration-1] = random_state
    print(list_random_param1)
    print(list_random_param2)
    result_mean_full = []
    result_mean_std = []
    for random_val1, random_val2 in zip(list_random_param1, list_random_param2):
        data_train, data_validation, classes_train, classes_validation = train_test_split(data_input, classes, test_size=0.3, random_state=random_val1, stratify=classes)
        # # # Standardization
        # scaling = StandardScaler()
        # scaling.fit(data_train, classes_train)
        # data_train = scaling_data(scaling, data_train)
        # data_validation = scaling_data(scaling, data_validation)

        classifier = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=random_val2, n_jobs=-1)
        # Fit the model to the training data
        classifier.fit(data_train, classes_train)
        # Predicting classes across the entire validation
        test_predictions = classifier.predict(data_validation)
        matrix_confusion = confusion_matrix(classes_validation, test_predictions)
        tss, tss_values = calculate_tss(matrix_confusion)
        print(f"TSS :{tss}")
        print(f"TSS cible :{tss_values[index_target]}")
        list_tss.append(tss)
        list_tss_exo.append(tss_values[index_target])
        # Évaluer le modèle
        result = permutation_importance(classifier, data_validation, classes_validation, n_repeats=5, random_state=random_state, n_jobs=-1)
        result_mean_full.append(result.importances_mean)
        result_mean_std.append(result.importances_std)

    print("TSS value for the random parameter chosen")
    print(f"TSS mean for {len(list_random_param1)} test is:")
    print(np.mean(list_tss))
    list_tss = [item for item in list_tss]
    list_tss_exo = [item for item in list_tss_exo]
    pyplot.plot(list_tss, color="coral", linewidth=.5, label='TSS global')
    pyplot.plot(list_tss_exo, color="green", linewidth=.5, label='TSS target')

    pyplot.plot(np.full(100, np.mean(list_tss)), ':', color="coral", label=f'mean ({np.around(np.mean(list_tss), 3)})')
    pyplot.plot(np.full(100, np.mean(list_tss_exo)), ':', color="green", label=f'mean ({np.around(np.mean(list_tss_exo), 3)})')
    pyplot.legend()
    pyplot.ylabel("TSS score")
    pyplot.xlabel("Combination of sklearn parameters change (Random_State and train_test_split)")
    pyplot.title('Importance of template size ')
    pyplot.title('Variation of TSS score based on use of template detection')
    pyplot.show()

    # Sélection des features les plus importants
    imp_features = result_permutation_importance_features(result_mean_full, result_mean_std, data_input.columns)
    selected_features = imp_features.index.tolist()
    return selected_features


# Recursive feature elimination with cross-validation
def selection_features_RFECV(classifier, data_input, classes, cv):
    kappa_scorer = make_scorer(cohen_kappa_score)
    classifier_selected = RFECV(
        estimator=classifier,
        step=1,
        cv=cv,
        scoring="balanced_accuracy",
        min_features_to_select=1,
        n_jobs=-1,
    )
    classifier_selected.fit(data_input, classes)
    print(f"Optimal number of features with RFECV: {classifier_selected.n_features_}")

    pyplot.figure()
    pyplot.xlabel("Number of features selected")
    pyplot.ylabel("Mean CV balanced accuracy")
    pyplot.errorbar(
        x=classifier_selected.cv_results_["n_features"],
        y=classifier_selected.cv_results_["mean_test_score"],
        yerr=classifier_selected.cv_results_["std_test_score"],
    )
    pyplot.title("Recursive Feature Elimination \nwith cross validation")
    pyplot.show()
    return classifier_selected.feature_names_in_[classifier_selected.support_].tolist()

# List features by importance for the model
def graphe_importance_features(classifier, all_features):
    importances = classifier.feature_importances_
    # # Créer un DataFrame pour les importances
    feature_importances = pd.DataFrame({'feature': all_features, 'importance': importances})
    # Trier les importances par ordre décroissant
    feature_importances = feature_importances.sort_values(by='importance', ascending=False)
    pyplot.figure(figsize=(10, 6))
    pyplot.bar(feature_importances['feature'], feature_importances['importance'])
    pyplot.ylabel('Importance')
    pyplot.xlabel('Indices')
    pyplot.title('Importance des indices')
    pyplot.xticks(rotation=45, ha='right', fontsize=8)
    pyplot.show()

# Write resultat of classification
def write_result_classification(data_pred, geometry, ypred, yproba, labels, path_output, file_data_to_predict="", output_name_classification="", filter_class=None):
    #list_proba = [f'proba_class_{i}' for i in list(labels.keys())]
    list_proba = [f'proba_{class_value}' for class_value in list(labels.values())]
    # # Fusion des résultats avec la gdb
    ypred_df = pd.DataFrame(data = ypred, columns = ['classvalue'], index = data_pred.index.copy())
    # Ajout de la colonne "classname" en fonction des "classvalue"
    ypred_df['classname'] = ypred_df['classvalue'].map(labels).astype(str)


    final_df = pd.merge(data_pred, ypred_df, how = 'left', left_index = True, right_index = True)

    if (yproba is not None):
        # Ajouter les champs de probabilités des classes
        proba_df = pd.DataFrame(yproba, columns=list_proba, index=data_pred.index.copy())
        final_df = pd.merge(final_df, proba_df, how = 'left', left_index = True, right_index = True)
        # columns_to_keep+=list_proba

    if filter_class is not None:
        final_df = final_df[final_df["classvalue"].isin(filter_class)]
        #final_df = final_df[final_df["classvalue"] == filter_class]

    final_gdf = gpd.GeoDataFrame(final_df, crs="EPSG:2975", geometry=geometry)

    if os.path.isdir(path_output): # dans le cas où on parcourt un répertoire
        file_output = file_data_to_predict.split("/")[-1]
        file_output = file_output.replace(".gpkg", output_name_classification+".gpkg")
        final_gdf.to_file(path_output+"/"+file_output, driver="GPKG")
    else:
        final_gdf.to_file(path_output, driver="GPKG")

# Merge gpkg files to write a large file and avoid memory issues
def merge_gpkg_files(directory, output_path, output_filename):
    # List to store all GeoDataFrames
    gdf_list = []

    # Iterate through all files in the directory
    for file in os.listdir(directory):
        if file.endswith(".gpkg"):
            file_path = os.path.join(directory, file)
            print(f"Lecture du fichier : {file_path}")
            gdf = gpd.read_file(file_path)
            gdf_list.append(gdf)

    # Merging all GeoDataFrames into one
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))

    # Writing the merged GeoDataFrame to a GPKG file
    output_file_path = os.path.join(output_path, output_filename)
    merged_gdf.to_file(output_file_path, driver="GPKG")

    # Deletes old files
    for file in os.listdir(directory):
        os.remove(directory+"/"+file)
