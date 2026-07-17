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
        self.addParameter(QgsProcessingParameterRasterLayer('ClipRasterByMaskLayer', 'clip_raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('ClipVectorByMaskLayer', 'clip_vector', defaultValue=None))
        
        self.addParameter(QgsProcessingParameterRasterLayer('bndvi', 'bndvi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('brightness', 'brightness', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('cri', 'cri', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('exg', 'exg', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gi', 'gi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gli', 'gli', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('haralick_texture_simple', 'haralick_texture_simple', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('hrfi', 'hrfi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('myi', 'myi', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('rgv', 'rgv', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ri', 'ri', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('sfs_texture', 'sfs_texture', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('vari', 'vari', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ngrdi', 'ngrdi', defaultValue=None))
        

    def processAlgorithm(self, parameters, context, model_feedback):
        # Utilisation d'un feedback multi-étape pour ajuster les rapports de progression
        feedback = QgsProcessingMultiStepFeedback(0, model_feedback)
        results = {}
        outputs = {}

        # Après avoir utilisé les fichiers, nous pouvons les supprimer physiquement du disque
        self.delete_file_from_disk(parameters, 'ClipRasterByMaskLayer', context, 'raster')
        self.delete_file_from_disk(parameters, 'ClipVectorByMaskLayer', context, 'vector')
        
        self.delete_file_from_disk(parameters, 'bndvi', context, 'raster')
        self.delete_file_from_disk(parameters, 'brightness', context, 'raster')
        self.delete_file_from_disk(parameters, 'cri', context, 'raster')
        self.delete_file_from_disk(parameters, 'exg', context, 'raster')
        self.delete_file_from_disk(parameters, 'gi', context, 'raster')
        self.delete_file_from_disk(parameters, 'gli', context, 'raster')
        self.delete_file_from_disk(parameters, 'haralick_texture_simple', context, 'raster')
        self.delete_file_from_disk(parameters, 'hrfi', context, 'raster')
        self.delete_file_from_disk(parameters, 'myi', context, 'raster')
        self.delete_file_from_disk(parameters, 'rgv', context, 'raster')
        self.delete_file_from_disk(parameters, 'ri', context, 'raster')
        self.delete_file_from_disk(parameters, 'sfs_texture', context, 'raster')
        self.delete_file_from_disk(parameters, 'vari', context, 'raster')
        self.delete_file_from_disk(parameters, 'ngrdi', context, 'raster')

        return results

    def delete_file_from_disk(self, parameters, param_name, context, type_file):
        # """Supprime physiquement le fichier du disque si le fichier existe."""
        # layer = self.parameterAsRasterLayer(parameters, param_name, context)
        # file_path = self.parameterAsRasterLayer(context, layer).source()
        
        if type_file == 'raster':
            layer = self.parameterAsRasterLayer(parameters, param_name, context)
        elif type_file == 'vector':
            layer = self.parameterAsVectorLayer(parameters, param_name, context)
            
        if layer is not None:
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
        return 'remove_temp_files'

    def displayName(self):
        return 'remove_temp_files'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Model()