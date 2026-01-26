"""Edge inference helper using ONNX Runtime."""

from __future__ import annotations

import argparse
import numpy as np
import onnxruntime as ort
from PIL import Image


def preprocess(image_path: str) -> np.ndarray:
    image = Image.open(image_path).resize((224, 224))
    array = np.array(image).astype("float32") / 255.0
    array = np.transpose(array, (2, 0, 1))  # channel first
    return np.expand_dims(array, axis=0)


def run_inference(model_path: str, image_path: str) -> np.ndarray:
    session = ort.InferenceSession(
        model_path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: preprocess(image_path)})
    return outputs[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()

    result = run_inference(args.model, args.image)
    print("Top-5 logits:", result[0][:5])
