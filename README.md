# ReMiNat-remote-sensing-invasive-species
Remote Sensing treatments for detection of alien invasive plants species with very high-resolution image (project ReMiNat: restauration des milieu naturels de la Réunion)

The project use model builder of QGIS with OrfeToolBox and Python with scikit-learn.

*ReMiNat-remote-sensing-invasive-species* a été développé par Antoine Sensier ([*UMR PVPMT*](https://umr-pvbmt.cirad.fr) / [*CIRAD*](https://www.cirad.fr)).

# Decription

1_image_processing:
   Processing steps to be performed in sequence using the QGIS Graphical Modeler to extract spectral, textural, and morphological indices from the image, can use also Digital Height Model and Digital Elevation Model.
   - 0_modele_buffers_sample.model3: Creation of buffers (dissolved) based on points collected in the field for model training/testing
   - 1_model_segmentation_generic_region.model3: Segmentation of the image with dividing the image according to a grid provided as input(maximum size recommanded is 250m for an image with a resolution of 5cm/pixel)
      GenericRegionMerging treatment require configuration with samples
   - 2_model_indices_radio_textures.model3: Calcul of radiometric vegetation indices and textural indices with the 3 originals bands of the image (RGB)
      HaralickTextureExtraction treatment require configuration with samples
  - 3_model_zonal_stat_indices.model3: Statistics (mean, median, standard deviation) on each polygons segmentation (step 1) with each indice calculated on step 2 
   - 1_and_2_and_3_compute_segmentation_indices_zonal_stat_features.model3: combining steps 1,  2 and 3 into a single yreatment
   - 2_and_3_compute_indices_zonal_stat_features.model3: Combining steps 2 and 3 into a single treatment
   - irc folder: same files but with Infra-red band added on the image, so it's alse calcul specifics radiometric indices with infra-red
   - python folder: python file to add on Processing Toolbox, used in model builder scripts

2_machine_learing:
   Python scripts to train/test the model with sample and make the prediction
   - 1_training_classification.py: Script to train/test a model for classify vegetation
   - 2_prediction_classification.py: Script for classification prediction using a previously trained model
   - functions_machine_learning.py: List of functions used in 1_train_classification and 2_prediction_classification scripts

Diagram of the main steps in the process:
<img width="1000" height="862" alt="process_classification_github" src="https://github.com/user-attachments/assets/aab63bec-9e23-4102-a519-e3a65525eec9" />

# Documentation

TODO

# Requirements

1_image_processing:
   - QGIS 3.4 minimum
   - Installation of OrfeoToolBox on QGIS
   - Install plugin on QGIS
   - Download OrfeoToolBox on https://www.orfeo-toolbox.org/download/ (minimum 9.0.0)
       - Link repository downloaded on QGIS Settings - Processing - Provider - OTB: (change the root "D:\" with your repository)
           - OTB application folder: D:\OTB-9.0.0-Win64\lib\otb\applications
           - OTB folder: D:\OTB-9.0.0-Win64\lib\otb\applications
        - If GenericRegionMerging doesn't appear on QGIS Processing Toolbox, follow these instructions: https://gitlab.orfeo-toolbox.org/orfeotoolbox/otb-qgis-plugin/-/work_items/14#note_115105	
   - Python and modeler script imbriqued in the QGIS Toolbox (need to be added on Processing Toolbox):
      - 1_image_processing/python/remove_temp_files_seg_generic.py
      - 1_image_processing/python/remove_temp_files.py
      - 1_image_processing/1_model_segmentation_generic_region.model3
      - 1_image_processing/2_model_indices_radio_textures.model3
      - 1_image_processing/3_model_zonal_stat_indices.model3

2_machine_learing:
   - Python 3.9 minimum
   - Libraries used are all in functions.py script

# Contact

*Author*: Antoine Sensier (antoine.sensier@gmail.com)

*Coordination*: Mathieu Rouget (mathieu.rouget@cirad.fr)
