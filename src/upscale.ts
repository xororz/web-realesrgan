import * as tf from "@tensorflow/tfjs";
import Image from "./image";

export default async function upscale(
  image: Image,
  model: any
): Promise<Image> {
  const result = tf.tidy(() => {
    const tensor = img2tensor(image);
    const result = model.predict(tensor) as tf.Tensor;
    return result;
  });
  const resultImage = await tensor2img(result);
  tf.dispose(result);
  return resultImage;
}

function img2tensor(image: Image): tf.Tensor {
  let arr = new Float32Array(image.width * image.height * 3);
  for (let i = 0; i < image.width * image.height; i++) {
    arr[i * 3] = image.data[i * 4] / 255;
    arr[i * 3 + 1] = image.data[i * 4 + 1] / 255;
    arr[i * 3 + 2] = image.data[i * 4 + 2] / 255;
  }
  let tensor = tf.tensor4d(arr, [1, image.height, image.width, 3]);
  return tensor;
}

async function tensor2img(tensor: tf.Tensor): Promise<Image> {
  let [_, height, width, __] = tensor.shape;
  let arr = await tensor.data();
  tensor.dispose();
  let clipped = new Uint8Array(
    arr.map((x) => {
      x = Math.min(1, Math.max(0, x));
      return Math.floor(x * 255);
    })
  );
  let image = new Image(width, height);
  for (let i = 0; i < width * height; i++) {
    image.data[i * 4] = clipped[i * 3];
    image.data[i * 4 + 1] = clipped[i * 3 + 1];
    image.data[i * 4 + 2] = clipped[i * 3 + 2];
    image.data[i * 4 + 3] = 255;
  }
  return image;
}
