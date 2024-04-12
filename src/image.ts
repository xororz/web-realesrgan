export default class Image {
  width: number;
  height: number;
  data: Uint8Array;
  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.data = new Uint8Array(width * height * 4);
  }
  getImageCrop(
    x: number,
    y: number,
    image: Image,
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ) {
    for (let j = y1; j < y2; j++) {
      for (let i = x1; i < x2; i++) {
        let index = (y + j - y1) * this.width * 4 + (x + i - x1) * 4;
        let imageIndex = j * image.width * 4 + i * 4;
        this.data[index] = image.data[imageIndex];
        this.data[index + 1] = image.data[imageIndex + 1];
        this.data[index + 2] = image.data[imageIndex + 2];
        this.data[index + 3] = image.data[imageIndex + 3];
      }
    }
  }
}
