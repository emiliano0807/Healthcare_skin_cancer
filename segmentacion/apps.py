import os
from django.apps import AppConfig
from django.conf import settings
import tensorflow as tf

class SegmentacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'segmentacion'
    
    # Definimos las variables para los dos modelos
    model_seg = None   # Segmentación (U-Net)
    model_clf = None   # Clasificación (MobileNet)

    def ready(self):
        if os.environ.get('RUN_MAIN') or 'RUN_MAIN' not in os.environ:
            base_dir = os.path.join(settings.BASE_DIR, 'segmentacion', 'ml_models')
            
            # 1. Cargar Modelo de Segmentación
            path_seg = os.path.join(base_dir, 'skin_cancer_unet.h5')
            if os.path.exists(path_seg):
                try:
                    self.model_seg = tf.keras.models.load_model(path_seg)
                    print("✅ Modelo U-Net (Dibujo) cargado.")
                except Exception as e:
                    print(f"❌ Error U-Net: {e}")

            # 2. Cargar Modelo de Clasificación
            path_clf = os.path.join(base_dir, 'skin_cancer_classifier.h5')
            if os.path.exists(path_clf):
                try:
                    self.model_clf = tf.keras.models.load_model(path_clf)
                    print("✅ Modelo Classifier (Diagnóstico) cargado.")
                except Exception as e:
                    print(f"❌ Error Classifier: {e}")