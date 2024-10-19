export default class Image {
  width: number;
  height: number;
  data: Uint8Array;
  constructor(
    width: number,
    height: number,
    data = new Uint8Array(width * height * 4)
  ) {
    this.width = width;
    this.height = height;
    this.data = data;
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
    const width = x2 - x1;
    for (let j = 0; j < y2 - y1; j++) {
      const destIndex = (y + j) * this.width * 4 + x * 4;
      const srcIndex = (y1 + j) * image.width * 4 + x1 * 4;
      this.data.set(
        image.data.subarray(srcIndex, srcIndex + width * 4),
        destIndex
      );
    }
  }
  padToTileSize(tileSize: number) {
    let newWidth = this.width;
    let newHeight = this.height;
    if (this.width < tileSize) {
      newWidth = tileSize;
    }
    if (this.height < tileSize) {
      newHeight = tileSize;
    }
    if (newWidth === this.width && newHeight === this.height) {
      return;
    }
    const newData = new Uint8Array(newWidth * newHeight * 4);
    for (let y = 0; y < this.height; y++) {
      const srcStart = y * this.width * 4;
      const destStart = y * newWidth * 4;
      newData.set(
        this.data.subarray(srcStart, srcStart + this.width * 4),
        destStart
      );
    }
    if (newWidth > this.width) {
      const rightColumnIndex = (this.width - 1) * 4;
      for (let y = 0; y < this.height; y++) {
        const destRowStart = y * newWidth * 4;
        const srcPixelIndex = y * this.width * 4 + rightColumnIndex;
        const padPixel = this.data.subarray(srcPixelIndex, srcPixelIndex + 4);
        for (let x = this.width; x < newWidth; x++) {
          const destPixelIndex = destRowStart + x * 4;
          newData.set(padPixel, destPixelIndex);
        }
      }
    }
    if (newHeight > this.height) {
      const bottomRowStart = (this.height - 1) * newWidth * 4;
      const bottomRow = newData.subarray(
        bottomRowStart,
        bottomRowStart + newWidth * 4
      );
      for (let y = this.height; y < newHeight; y++) {
        const destRowStart = y * newWidth * 4;
        newData.set(bottomRow, destRowStart);
      }
    }
    this.width = newWidth;
    this.height = newHeight;
    this.data = newData;
  }
  cropToOriginalSize(width: number, height: number) {
    const newData = new Uint8Array(width * height * 4);
    for (let y = 0; y < height; y++) {
      const srcStart = y * this.width * 4;
      const destStart = y * width * 4;
      newData.set(
        this.data.subarray(srcStart, srcStart + width * 4),
        destStart
      );
    }
    this.width = width;
    this.height = height;
    this.data = newData;
  }
}
