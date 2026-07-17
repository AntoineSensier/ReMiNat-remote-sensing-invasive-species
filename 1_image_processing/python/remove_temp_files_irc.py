import os
import time
from qgis.core import QgsProcessing
from qgis.core import QgsApplication
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProject
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
import processing


class Model(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('bndvi', 'bndvi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('brightness', 'brightness', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('cri', 'cri', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('exg', 'exg', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gi', 'gi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gli', 'gli', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Haralick_simple', 'haralick_simple', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Haralick_advanced', 'haralick_advanced', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Sfstextures', 'SFSTextures', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('hrfi', 'hrfi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('myi', 'myi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('rgv', 'rgv', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ri', 'ri', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('sfs_texture', 'sfs_texture', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('vari', 'vari', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('evi', 'EVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gdvi', 'GDVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('msr', 'MSR', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ndvi', 'NDVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('cigreen', 'Cigreen', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('cvi', 'CVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('savi', 'SAVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ri2', 'RI2', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Ndwi2', 'NDWI2', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Rvi', 'RVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Bi2', 'BI2', defaultValue=None))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Utilisation d'un feedback multi-étape pour ajuster les rapports de progression
        feedback = QgsProcessingMultiStepFeedback(0, model_feedback)
        results = {}
        outputs = {}

        # Après avoir utilisé les fichiers, nous pouvons les supprimer physiquement du disque
        self.delete_file_from_disk(parameters, 'bndvi', context)
        self.delete_file_from_disk(parameters, 'brightness', context)
        self.delete_file_from_disk(parameters, 'cri', context)
        self.delete_file_from_disk(parameters, 'exg', context)
        self.delete_file_from_disk(parameters, 'gi', context)
        self.delete_file_from_disk(parameters, 'gli', context)
        self.delete_file_from_disk(parameters, 'Haralick_simple', context)
        self.delete_file_from_disk(parameters, 'Haralick_advanced', context)
        self.delete_file_from_disk(parameters, 'Sfstextures', context)
        self.delete_file_from_disk(parameters, 'hrfi', context)
        self.delete_file_from_disk(parameters, 'myi', context)
        self.delete_file_from_disk(parameters, 'rgv', context)
        self.delete_file_from_disk(parameters, 'ri', context)
        self.delete_file_from_disk(parameters, 'vari', context)
        self.delete_file_from_disk(parameters, 'evi', context)
        self.delete_file_from_disk(parameters, 'gdvi', context)
        self.delete_file_from_disk(parameters, 'msr', context)
        self.delete_file_from_disk(parameters, 'ndvi', context)
        self.delete_file_from_disk(parameters, 'cigreen', context)
        self.delete_file_from_disk(parameters, 'cvi', context)
        self.delete_file_from_disk(parameters, 'savi', context)
        self.delete_file_from_disk(parameters, 'ri2', context)
        self.delete_file_from_disk(parameters, 'Ndwi2', context)
        self.delete_file_from_disk(parameters, 'Rvi', context)
        self.delete_file_from_disk(parameters, 'Bi2', context)

        return results

    def delete_file_from_disk(self, parameters, param_name, context):
        # """Supprime physiquement le fichier du disque si le fichier existe."""
        # layer = self.parameterAsRasterLayer(parameters, param_name, context)
        # file_path = self.parameterAsRasterLayer(context, layer).source()
        layer = self.parameterAsRasterLayer(parameters, param_name, context)
        file_path = layer.source()
        layer_temp = context.takeResultLayer(layer.id())
        QgsProject.instance().removeMapLayer(layer.id())        
        del(layer)
        del(layer_temp)
        # context.temporaryLayerStore().removeAllMapLayers()
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Le fichier {file_path} a été supprimé avec succès.")
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier {file_path}: {str(e)}")
        else:
            print(f"Le fichier {file_path} n'existe pas ou a déjà été supprimé.")

    def name(self):
        return 'remove_temp_files_irc'

    def displayName(self):
        return 'remove_temp_files_irc'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Model()