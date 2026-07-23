# ReMiNat-remote-sensing-invasive-species
Remote Sensing treatments for detection of alien invasive plants species with very high-resolution image (project ReMiNat : restauration des milieu naturels de la Réunion)

The project use model builder of QGIS with OrfeToolBox and Python with scikit-learn.

*ReMiNat-remote-sensing-invasive-species* a été développé par Antoine Sensier ([*UMR PVPMT*](https://umr-pvbmt.cirad.fr) / [*CIRAD*](https://www.cirad.fr)).

# Decription
TODO ADD IRC AND PYTHON scripts

1_image_processing:
   Processing steps to be performed in sequence using the QGIS Graphical Modeler to extract spectral, textural, and morphological indices from the image, can use also Digital Height Model and Digital Elevation Model.
- TODO list files

2_machine_learing:
   Python scripts to train/test the model with sample and make the prediction.
- TODO list files

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
       - Link repository downloaded on QGIS Settings - Processing - Provider - OTB : (change the root "D:\")
           - OTB application folder : D:\OTB-9.0.0-Win64\lib\otb\applications
           - OTB folder : D:\OTB-9.0.0-Win64\lib\otb\applications
        - If GenericRegionMerging doesn't appear on QGIS Processing Toolbox, follow these instructions : https://gitlab.orfeo-toolbox.org/orfeotoolbox/otb-qgis-plugin/-/work_items/14#note_115105	
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

*Author* : Antoine Sensier (antoine.sensier@gmail.com)

*Coordination* : Mathieu Rouget (mathieu.rouget@cirad.fr)
