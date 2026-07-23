# -*- coding: utf-8 -*-
"""
Script for classification prediction using a previously trained model
Require training with features calculated from the image
Inputs:
    - training data (vector polygons)
Outputs:
    - model for prediction
    - confusion_matrix.csv (opitonal)

Author : Antoine Sensier, CIRAD, 2026

"""
from functions_machine_learning import *

# Inputs
path_root = 'D:/Data' # to be changed

path_data_sample = path_root+'/sample/sample_zonal_stat.gpkg' # to be changed

data_input = gpd.read_file(path_data_sample)
print(len(data_input))

# Outputs
path_model = path_root+'/models1'
# path_scale = path_root+'/models/model_rf_norm_scale.pkl'
os.makedirs(path_model, exist_ok=True)
name_model_output = 'model_rf_v1.pkl'

path_matrix_confusion = path_root+'/matrices_confusion1'
os.makedirs(path_matrix_confusion, exist_ok=True)
name_matrix_output = 'm_confusion_rf.csv'

# Separate features and labels
classes = data_input['classvalue']
labels = data_input.drop_duplicates(subset=['classvalue']).set_index('classvalue')['classname'].to_dict()
labels = dict(sorted(labels.items())) # to sort the classes by value
counts_df = data_input['classname'].value_counts()
counts_df.columns = ['classname', 'count']
print(counts_df)

data_input = data_input.drop(columns=['geometry', 'fid', 'comment', 'classvalue', 'classname', 'layer', 'path','date'], errors='ignore')
# Column to be retained; may be useful for post-classification
cols_to_keep = data_input.columns.tolist() #['area', 'mnc_mean','elongation']

random_state = 42 # fix random paramater for reproductibility
print(len(data_input.columns))

cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state) # for cross validation in 4 splits, shuffled randomly but in a reproducible manner
# Stratified by class and split the data into training and test sets, 75% / 25%, can be changed
data_train, data_validation, classes_train, classes_validation = train_test_split(data_input, classes, test_size=0.25, shuffle=True, stratify=classes, random_state=random_state)

# Reduction of feature redundancy on train data to avoid biais
data_train = remove_correlated_features(data_train, 0.95) # Remove data correladed with more than 95%, can be changer by other value
data_validation = data_validation[data_train.columns.tolist()]
data_input = data_input[data_train.columns.tolist()]

# Data standardization, optional
# scaling = StandardScaler()
# scaling.fit(data_train, classes_train)
# data_train = scaling_data(scaling, data_train)
# data_validation = scaling_data(scaling, data_validation)
# data_input = scaling_data(scaling, data_input)

# # Show LDA on training data to see classes separability
lda = LinearDiscriminantAnalysis(n_components=3) #/3D
classes_uniques = np.unique(classes_train)
colors = pyplot.cm.tab20(np.linspace(0, 1, len(classes_uniques)))  # Generate an automatic color palette

X_lda = lda.fit_transform(data_train, classes_train)
print(np.round(lda.explained_variance_ratio_, 3)) # Print the explained variance ratio of each component
print(f"Cumulative explained variance on training data : {np.round(sum(lda.explained_variance_ratio_), 3)*100}")
silhouette_avg = silhouette_score(X_lda, classes_train)
print(f"Silhouette Score : {np.round(silhouette_avg, 3)}")
fig = pyplot.figure()

# 3D
ax = fig.add_subplot(111, projection='3d')
for i, color in zip(classes_uniques, colors):
    ax.scatter(
        X_lda[classes_train == i, 0], X_lda[classes_train == i, 1],X_lda[classes_train == i, 2],  alpha=0.8, label=labels[i], color=color
    )
ax.legend(loc="best", shadow=False, scatterpoints=1)
ax.set_title("LDA of classes dataset")
expl_var = lda.explained_variance_ratio_
ax.set_xlabel(f"LD1 ({expl_var[0]*100:.1f}%)")
ax.set_ylabel(f"LD2 ({expl_var[1]*100:.1f}%)")
if len(expl_var) > 2:
    ax.set_zlabel(f"LD3 ({expl_var[2]*100:.1f}%)")
else:
    ax.set_zlabel("LD3")
pyplot.show()

# Type of classification
# classifier = LinearSVC(C=1.0, penalty='l2', class_weight="balanced", random_state=random_state, max_iter=10000)
# classifier = SVC(kernel='linear', class_weight='balanced', random_state=random_state, probability=True)  #  try kernel='linear' ou 'rbf'
# classifier = GaussianNB()
# classifier = LogisticRegression(random_state=random_state)
# classifier = MLPClassifier(hidden_layer_sizes=(200,), activation='relu', solver='adam', max_iter=1000, random_state=random_state) #solver='adam' 'lbfgs'
# classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=random_state)
# classifier = HistGradientBoostingClassifier(
#     max_iter=300,
#     learning_rate=0.05,
#     max_leaf_nodes=31,
#     min_samples_leaf=20,  # important pour la généralisation spatiale
#     class_weight='balanced',
#     random_state=random_state
# )
# classifier = DecisionTreeClassifier(criterion="gini", max_depth=None)
# classifier = LGBMClassifier(
#     num_leaves=63,
#     max_depth=-1,
#     min_child_samples=5,
#     n_estimators=1000,
#     class_weight="balanced",
#     random_state=random_state
# )
classifier = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=random_state, n_jobs=-1)

# Selection of features
selected_features = selection_features_from_model(classifier, data_train, classes_train, threshold=0.01)
# selected_features = selection_features_permutation_importance(data_train, classes_train, data_validation, classes_validation, 100, random_state)
# selected_features = selection_features_permutation_CV_robust(
#     data_train, classes_train,
#     cv=cv,
#     nb_repeats_cv=25,   # replications of the full cross-validation (CV)
#     nb_repeats_perm=10,  # internal permutations
#     random_state=random_state
# )
# selected_features = selection_features_RFECV(classifier, data_train, classes_train, cv)
print("Selected features:")
print(selected_features)
print(len(selected_features))
data_train_selected = data_train[selected_features]
data_validation_selected = data_validation[selected_features]


# # Ajust the model
classifier.fit(data_train_selected, classes_train)

# List features by importance for the model
graphe_importance_features(classifier, selected_features)


# Evaluate the model
prediction_selected = classifier.predict(data_validation_selected)
print("Scores model :")
scores = assessment_model(
        classes_validation,
        prediction_selected,
        labels,
        True, # Write or note the matrix
        path_matrix_confusion+'/'+name_matrix_output
    )
print(labels)


scores_cv = cross_val_score(classifier, data_input[selected_features], classes, cv=cv, scoring='accuracy')
print("Scores for each fold :", scores_cv)
print(f"Average score across cross-validation folds   : {scores_cv.mean()}")
scoring = {
    'kappa': make_scorer(cohen_kappa_score),
    'tss': make_scorer(tss_score),
    'accuracy': make_scorer(accuracy_score)
}
results = cross_validate(classifier, data_input[selected_features],classes, cv=cv, scoring=scoring)

classifier.fit(data_input[selected_features], classes) # Train on 100% if model is validated, optional

# Saving the model for prediction
#  pickle.dump(scaling, open(path_scale, 'wb')) # If standardization
pickle.dump(classifier, open(path_model+'/'+name_model_output, "wb"))

