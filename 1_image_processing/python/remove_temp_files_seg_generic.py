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
        self.addParameter(QgsProcessingParameterRasterLayer('ClipRasterByMaskLayer1', 'raster_in', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Genericregionmerging', 'raster_out', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('PolygonizeRasterToVector', 'vector_out', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Utilisation d'un feedback multi-étape pour ajuster les rapports de progression
        feedback = QgsProcessingMultiStepFeedback(0, model_feedback)
        results = {}
        outputs = {}

        # Après avoir utilisé les fichiers, nous pouvons les supprimer physiquement du disque
        self.delete_file_from_disk(parameters, 'ClipRasterByMaskLayer1', context, 'raster')
        self.delete_file_from_disk(parameters, 'Genericregionmerging', context, 'raster')
        self.delete_file_from_disk(parameters, 'PolygonizeRasterToVector', context, 'vector')
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
        else:
             print(f"La couche {layer} n'existe pas.")

    def name(self):
        return 'remove_temp_files_seg_generic'

    def displayName(self):
        return 'remove_temp_files_seg_generic'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Model()