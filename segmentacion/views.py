from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import numpy as np
from PIL import Image
import io
import base64
import os
import tensorflow as tf
import gc # Garbage Collector para liberar memoria

# Variables globales para caché (opcional, pero en free tier mejor cargar y limpiar)
# Para el plan GRATIS de Render, recomiendo cargar, predecir y limpiar.
# Es un poco más lento, pero asegura que no se rompa por falta de RAM.

def index(request):
    return render(request, 'index.html')

class SkinAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'error': 'No hay imagen'}, status=400)

        model_seg = None
        model_clf = None

        try:
            # 1. Procesar Imagen Base
            img_original = Image.open(file_obj).convert('RGB')
            original_size = img_original.size
            
            # Ruta base de modelos
            base_dir = os.path.join(settings.BASE_DIR, 'segmentacion', 'ml_models')

            # -------------------------------------------------------
            # FASE 1: SEGMENTACIÓN (Cargar -> Usar -> Borrar)
            # -------------------------------------------------------
            tf.keras.backend.clear_session() # Limpiar sesión anterior
            
            path_seg = os.path.join(base_dir, 'skin_cancer_unet.h5')
            model_seg = tf.keras.models.load_model(path_seg)
            
            # Preprocesar para U-Net
            img_seg_input = img_original.resize((128, 128))
            arr_seg = np.array(img_seg_input) / 255.0
            arr_seg = np.expand_dims(arr_seg, axis=0)

            # Predecir Segmentación
            pred_mask = model_seg.predict(arr_seg)
            mask = pred_mask[0, :, :, 0]
            
            # Liberar memoria U-Net INMEDIATAMENTE
            del model_seg
            gc.collect()
            tf.keras.backend.clear_session()

            # Procesar Máscara a Imagen
            mask_binary = (mask > 0.5).astype(np.uint8) * 255
            mask_pil = Image.fromarray(mask_binary).resize(original_size)
            mask_rgba = mask_pil.convert("RGBA")
            datas = mask_rgba.getdata()
            newData = []
            for item in datas:
                if item[0] == 0: 
                    newData.append((0, 0, 0, 0))
                else:
                    newData.append((255, 0, 0, 140))
            mask_rgba.putdata(newData)
            
            buffer = io.BytesIO()
            mask_rgba.save(buffer, format="PNG")
            mask_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # -------------------------------------------------------
            # FASE 2: CLASIFICACIÓN (Cargar -> Usar -> Borrar)
            # -------------------------------------------------------
            path_clf = os.path.join(base_dir, 'skin_cancer_classifier.h5')
            model_clf = tf.keras.models.load_model(path_clf)

            # Preprocesar para MobileNet
            img_clf_input = img_original.resize((224, 224))
            arr_clf = np.array(img_clf_input) / 255.0
            arr_clf = np.expand_dims(arr_clf, axis=0)

            # Predecir Clase
            pred_label = model_clf.predict(arr_clf)
            score = float(pred_label[0][0])

            # Liberar memoria Clasificador
            del model_clf
            gc.collect()
            tf.keras.backend.clear_session()

            # Lógica final
            threshold = 0.5
            is_malignant = score > threshold
            label_text = "MALIGNO (Alto Riesgo)" if is_malignant else "BENIGNO (Bajo Riesgo)"
            probability = score if is_malignant else 1 - score
            
            return Response({
                'status': 'success',
                'mask_base64': mask_b64,
                'diagnosis': label_text,
                'confidence': f"{probability*100:.1f}%",
                'is_danger': is_malignant
            })

        except Exception as e:
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=500)
        finally:
            # Limpieza final de seguridad
            gc.collect()