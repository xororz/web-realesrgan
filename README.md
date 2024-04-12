# web-realesrgan

Run Real-ESRGAN in the browser with tensorflow.js

## Usage

### Online Demo

[https://cappuccino.moe](https://cappuccino.moe)

![demo](./src/assets/demo.png)

### Accelaration

- WebGL: Enabled on most devices by default.
- WebGPU: Enabled on Chrome with `chrome://flags/#enable-unsafe-webgpu` flag or other browsers with WebGPU support. Much faster than WebGL.

### Development

```bash
npm install
npm run dev
```

## Credits

Pytorch model -> ONNX -> Tensorflow saved model -> Tensorflow.js

- [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)
- [PINTO0309/onnx2tf](https://github.com/PINTO0309/onnx2tf)
- [tensorflow/tfjs](https://github.com/tensorflow/tfjs)
