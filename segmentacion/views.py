from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.apps import apps
import numpy as np
from PIL import Image
import io
import base64

def index(request):
    return render(request, 'index.html')

class SkinAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({'error': 'No hay imagen'}, status=400)

        try:
            # Cargar imagen base una sola vez
            img_original = Image.open(file_obj).convert('RGB')
            original_size = img_original.size

            # Obtener los modelos cargados
            app_config = apps.get_app_config('segmentacion')
            model_seg = app_config.model_seg
            model_clf = app_config.model_clf

            if not model_seg or not model_clf:
                return Response({'error': 'Los modelos no están cargados completamente.'}, status=500)

            # --- TAREA 1: SEGMENTACIÓN (Dibujar la mancha) ---
            # U-Net suele usar 128x128
            img_seg_input = img_original.resize((128, 128))
            arr_seg = np.array(img_seg_input) / 255.0
            arr_seg = np.expand_dims(arr_seg, axis=0)

            pred_mask = model_seg.predict(arr_seg)
            mask = pred_mask[0, :, :, 0]

            # Crear imagen de máscara (Roja semitransparente)
            mask_binary = (mask > 0.5).astype(np.uint8) * 255
            mask_pil = Image.fromarray(mask_binary).resize(original_size)
            
            mask_rgba = mask_pil.convert("RGBA")
            datas = mask_rgba.getdata()
            newData = []
            for item in datas:
                if item[0] == 0: 
                    newData.append((0, 0, 0, 0)) # Transparente
                else:
                    newData.append((255, 0, 0, 140)) # Rojo translúcido
            mask_rgba.putdata(newData)

            # Guardar máscara en Base64
            buffer = io.BytesIO()
            mask_rgba.save(buffer, format="PNG")
            mask_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')


            # --- TAREA 2: CLASIFICACIÓN (Diagnosticar) ---
            # MobileNet suele usar 224x224
            img_clf_input = img_original.resize((224, 224))
            arr_clf = np.array(img_clf_input) / 255.0
            arr_clf = np.expand_dims(arr_clf, axis=0)

            pred_label = model_clf.predict(arr_clf)
            score = float(pred_label[0][0]) # 0 a 1

            # Lógica de decisión
            threshold = 0.5
            is_malignant = score > threshold
            
            label_text = "MALIGNO (Alto Riesgo)" if is_malignant else "BENIGNO (Bajo Riesgo)"
            probability = score if is_malignant else 1 - score
            
            # --- RESPUESTA FINAL ---
            return Response({
                'status': 'success',
                'mask_base64': mask_b64,       # Imagen sombreada
                'diagnosis': label_text,       # Texto diagnóstico
                'confidence': f"{probability*100:.1f}%", # Porcentaje
                'is_danger': is_malignant      # Booleano para colores en frontend
            })

        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=500)