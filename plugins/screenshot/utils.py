from typing import Any
import openvino as ov
import numpy as np
import cv2
import time


class ImageClassifier:
    def __init__(self):
        self.tag = {0: '非拍屏', 1: '拍屏'}
        core = ov.Core()
        classification_model_xml = "int8_openvino_model/best.xml"
        model = core.read_model(model=classification_model_xml)
        self.model = core.compile_model(model=model, device_name="CPU")
        self.output_layer = self.model.output(0)

    def classify(self, file_bytes: bytes) -> tuple[str, int | Any, float]:
        t = time.time()
        img = cv2.cvtColor(cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (1536, 1536))
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        result = self.model([image_data])[self.output_layer]
        predicted_class = np.argmax(result[0])
        confidence = np.max(result[0])
        return self.tag[predicted_class], confidence * 100, (time.time() - t) * 1000
