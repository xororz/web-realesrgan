<template>
  <!-- <div v-if="isDragOver" class="drag-mask">Drop your image here</div> -->
  <div
    ref="canvasContainer"
    class="canvas-container"
    :class="{
      'canvas-container': true,
      bg: true,
      dark: imgLoaded,
      'drag-over': isDragOver,
    }"
    @drop.prevent="handleDrop"
    @dragover.prevent="isDragOver = true"
    @dragleave="
      (e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) {
          isDragOver = false;
        }
      }
    "
    @mousedown="startDragging"
    @mouseup="stopDragging"
    @mousemove="dragImage"
    @wheel="resizeImage"
    @touchstart="touchStart"
    @touchmove="touchMove"
    @touchend="touchEnd"
  >
    <div v-if="!imgLoaded && !isDragOver" class="title">
      <div>SuperResolution in Your Browser</div>
      <img
        style="
          width: 50px;
          display: block;
          margin: auto;
          transform: translate(-18%, 0);
        "
        src="/demo/2.png"
        alt="favicon"
        class="favicon"
        @click="testdemo"
      />
    </div>
    <canvas ref="canvas"></canvas>
    <canvas ref="imgCanvas" style="display: none"></canvas>
    <button
      v-show="!imgLoaded"
      class="upload-button"
      @click="handleClick"
      :style="upload_button_style"
    >
      <div class="upload-container">
        <svg viewBox="0 0 24 24">
          <path
            d="M19 7v3h-2V7h-3V5h3V2h2v3h3v2h-3zm-3 4V8h-3V5H5a2 2 0 00-2 2v12c0 1.1.9 2 2 2h12a2 2 0 002-2v-8h-3zM5 19l3-4 2 3 3-4 4 5H5z"
            fill0="rgba(255, 182, 193, 1)"
            fill00="#ff568a"
            fill="white"
          ></path>
        </svg>
      </div>
    </button>
    <button v-show="imgLoaded" class="goback" @click="reloadPage">
      <svg width="24" height="24" viewBox="0 0 1024 1024">
        <g
          fill="rgba(255, 255, 255, 1)"
          stroke-width="50"
          stroke="rgba(255, 255, 255, 1)"
        >
          <path
            d="M511.4 175.3l-31.6 31.6-74.8 74.8-87.7 87.7-71.5 71.5-20.1 20.1c-7.1 7.1-13.9 14.3-18.1 23.7-11.2 25.4-6 53.9 13.6 73.7l13.2 13.2 62.7 62.7 86.8 86.8 80.8 80.8 44.7 44.7 2.1 2.1c6.7 6.7 18.9 7.2 25.5 0 6.6-7.2 7.1-18.3 0-25.5l-30.9-30.9-73.8-73.8-87.1-87.1-71.7-71.7-21.1-21.1-5.3-5.3-1.1-1.1-0.1-0.1c-0.3-0.3-3.9-4.4-2.4-2.6 1.3 1.7-0.1-0.2-0.3-0.5-0.8-1.2-1.5-2.4-2.2-3.6-0.3-0.6-0.7-1.2-1-1.9-0.3-0.6-1.3-3.3-0.5-1 0.7 2.3-0.7-2.4-0.9-3.1-0.4-1.4-1.7-6-0.7-2-0.5-1.9-0.3-4.2-0.3-6.2 0-0.1 0.3-4.8 0.3-4.8 0.5 0.1-0.7 3.6 0 0.7l0.6-2.7c0.3-1.2 2.3-6.2 0.5-2.2 0.8-1.7 1.6-3.4 2.6-5 0.6-0.9 4-5.1 1.3-2.2 1-1.1 1.9-2.2 3-3.3l0.2-0.2 1.2-1.2 14.3-14.3 63.6-63.6 86-86 79.8-79.8 44-44 2.1-2.1c6.7-6.7 7.2-18.9 0-25.5-7.4-6.3-18.6-6.8-25.7 0.3z"
          ></path>
          <path
            d="M804.6 494H432.9c-17.2 0-34.5-0.5-51.7 0h-0.7c-9.4 0-18.4 8.3-18 18 0.4 9.8 7.9 18 18 18h371.7c17.2 0 34.5 0.5 51.7 0h0.7c9.4 0 18.4-8.3 18-18-0.5-9.8-8-18-18-18z"
          ></path>
        </g>
      </svg>
    </button>
    <a
      href="https://github.com/xororz/web-realesrgan"
      v-show="imgLoaded"
      target="_blank"
    >
      <img src="/gh.png" alt="github" class="github" />
    </a>
    <div class="floating-menu" :style="menu_style" @mousedown.stop>
      <div>
        <div class="info" v-if="info">{{ info }}</div>
        <div class="progressbar" v-if="isProcessing || isDone">
          <progress max="100" :value="progress"></progress>
        </div>
      </div>
      <div class="opt" v-if="!isProcessing && !isDone">
        <div>
          <span class="description">Type</span>
          <select v-model="model_type">
            <option value="realesrgan">Real-ESRGAN</option>
            <option value="realcugan">Real-CUGAN</option>
          </select>
        </div>
        <div v-if="model_type === 'realesrgan'">
          <div>
            <span class="description">Model</span>
            <select v-model="model">
              <option
                v-for="modelOption in model_config.realesrgan.model"
                :key="modelOption"
                :value="modelOption"
              >
                {{ modelOption }}
              </option>
            </select>
          </div>
          <div>
            <span class="description">Scale</span>
            <select v-model="factor">
              <option
                v-for="factorOption in model_config.realesrgan.factor"
                :key="factorOption"
                :value="factorOption"
              >
                {{ factorOption }}
              </option>
            </select>
          </div>
          <div>
            <span class="description">Tile Size</span>
            <select v-model="tile_size">
              <option
                v-for="tileSizeOption in model_config.realesrgan.tile_size"
                :key="tileSizeOption"
                :value="tileSizeOption"
              >
                {{ tileSizeOption }}
              </option>
            </select>
          </div>
        </div>
        <div v-else-if="model_type === 'realcugan'">
          <div>
            <span class="description">Denoise</span>
            <select v-model="denoise">
              <option
                v-for="denoiseOption in model_config.realcugan.denoise[factor]"
                :key="denoiseOption"
                :value="denoiseOption"
              >
                {{ denoiseOption }}
              </option>
            </select>
          </div>
          <div>
            <span class="description">Scale</span>
            <select v-model="factor">
              <option
                v-for="factorOption in model_config.realcugan.factor"
                :key="factorOption"
                :value="factorOption"
              >
                {{ factorOption }}
              </option>
            </select>
          </div>
          <div>
            <span class="description">Tile Size</span>
            <select v-model="tile_size">
              <option
                v-for="tileSizeOption in model_config.realcugan.tile_size"
                :key="tileSizeOption"
                :value="tileSizeOption"
              >
                {{ tileSizeOption }}
              </option>
            </select>
          </div>
        </div>
        <div>
          <span class="description">Overlap</span>
          <select v-model="min_lap">
            <option>0</option>
            <option>4</option>
            <option>8</option>
            <option>12</option>
            <option>16</option>
            <option>20</option>
          </select>
        </div>
        <div>
          <span class="description">Run on</span>
          <select v-model="backend">
            <option value="webgl">WebGL</option>
            <option value="webgpu">WebGPU</option>
          </select>
        </div>
      </div>
      <div>
        <div>
          <button class="question-button" v-if="!isProcessing && !isDone">
            <a
              href="https://github.com/xororz/web-realesrgan/?tab=readme-ov-file#best-practice"
              target="_blank"
            >
              <svg
                viewBox="0 0 15 15"
                xmlns="http://www.w3.org/2000/svg"
                fill="#fff"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M7.5 1a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zm0 12a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11zm1.55-8.42a1.84 1.84 0 0 0-.61-.42A2.25 2.25 0 0 0 7.53 4a2.16 2.16 0 0 0-.88.17c-.239.1-.45.254-.62.45a1.89 1.89 0 0 0-.38.62 3 3 0 0 0-.15.72h1.23a.84.84 0 0 1 .506-.741.72.72 0 0 1 .304-.049.86.86 0 0 1 .27 0 .64.64 0 0 1 .22.14.6.6 0 0 1 .16.22.73.73 0 0 1 .06.3c0 .173-.037.343-.11.5a2.4 2.4 0 0 1-.27.46l-.35.42c-.12.13-.24.27-.35.41a2.33 2.33 0 0 0-.27.45 1.18 1.18 0 0 0-.1.5v.66H8v-.49a.94.94 0 0 1 .11-.42 3.09 3.09 0 0 1 .28-.41l.36-.44a4.29 4.29 0 0 0 .36-.48 2.59 2.59 0 0 0 .28-.55 1.91 1.91 0 0 0 .11-.64 2.18 2.18 0 0 0-.1-.67 1.52 1.52 0 0 0-.35-.55zM6.8 9.83h1.17V11H6.8V9.83z"
                />
              </svg>
            </a>
          </button>
        </div>
        <button
          class="run-button"
          v-if="!isProcessing && !isDone"
          @click="startTask"
        >
          <svg viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" fill="rgba(255, 255, 255, 1)"></path>
          </svg>
        </button>
      </div>
      <button class="save-button" v-if="isDone" @click="saveImage">
        <svg width="22" viewBox="0 -4 23.9 30">
          <path
            fill="#fff"
            d="M6.6 2.7h-4v13.2h2.7A2.7 2.7 0 018 18.6a2.7 2.7 0 002.6 2.6h2.7a2.7 2.7 0 002.6-2.6 2.7 2.7 0 012.7-2.7h2.6V2.7h-4a1.3 1.3 0 110-2.7h4A2.7 2.7 0 0124 2.7v18.5a2.7 2.7 0 01-2.7 2.7H2.7A2.7 2.7 0 010 21.2V2.7A2.7 2.7 0 012.7 0h4a1.3 1.3 0 010 2.7zm4 7.4V1.3a1.3 1.3 0 112.7 0v8.8L15 8.4a1.3 1.3 0 011.9 1.8l-4 4a1.3 1.3 0 01-1.9 0l-4-4A1.3 1.3 0 019 8.4z"
          ></path>
        </svg>
      </button>
    </div>
    <div
      class="dragLine"
      ref="dragLine"
      v-show="isDone"
      @mousedown.stop="startDraggingLine"
      @mousemove.stop="dragLine"
    >
      <div class="dragBall">
        <svg width="30" viewBox="0 0 27 20">
          <path fill="#ff3484" d="M9.6 0L0 9.6l9.6 9.6z"></path>
          <path fill="#5fb3e5" d="M17 19.2l9.5-9.6L16.9 0z"></path>
        </svg>
      </div>
    </div>
    <div v-if="!imgLoaded & !isDragOver" class="bottom-svg">
      <svg width="100%" viewBox="0 0 1920 140" class="_top-wave_vzxu7_106">
        <path
          fill="#76c8fe"
          d="M1920 0l-107 28c-106 29-320 85-533 93-213 7-427-36-640-50s-427 0-533 7L0 85v171h1920z"
          class="_sub-wave_vzxu7_117"
        ></path>
        <path
          fill="#009aff"
          d="M0 129l64-26c64-27 192-81 320-75 128 5 256 69 384 64 128-6 256-80 384-91s256 43 384 70c128 26 256 26 320 26h64v96H0z"
          class="_main-wave_vzxu7_113"
        ></path>
      </svg>
      <div class="demo">
        <div>No ideas? Try one of these:</div>
        <br />
        <div>
          <img class="demoimg" src="/demo/1.jpg" alt="demo" @click="testdemo" />
          <img class="demoimg" src="/demo/2.jpg" alt="demo" @click="testdemo" />
          <img class="demoimg" src="/demo/3.jpg" alt="demo" @click="testdemo" />
        </div>
      </div>
    </div>
    <!-- <div v-if="!imgLoaded" class="placeholder"></div> -->
  </div>
</template>

<script>
import Img from "./image";
import Module from "./imghelper";

export default {
  data() {
    return {
      dragging: false,
      touching: false,
      imgX: 0,
      imgY: 0,
      imgScale: 1,
      imgInitScale: 1,
      linePosition: 0,
      drawLine: false,
      draggingLine: false,
      imgLoaded: false,
      dpr: window.devicePixelRatio || 1,
      imgName: "output",
      img: new Image(),
      processedImg: new Image(),
      hasAlpha: false,
      touchStartImgX: null,
      touchStartImgY: null,
      touchStartX: null,
      touchStartY: null,
      touchStartDistance: null,
      imgScaleStart: 1,

      imgLoaded: false,
      input: null,
      output: null,
      isDragOver: false,
      isProcessing: false,
      isDone: false,
      progress: 0,
      model_type: "realcugan",
      model_config: {
        realesrgan: {
          model: ["anime_fast", "anime_plus", "general_fast", "general_plus"],
          factor: [4],
          tile_size: [64],
        },
        realcugan: {
          // factor: [2, 3, 4],
          factor: [2, 4],
          denoise: {
            2: [
              "conservative",
              "no-denoise",
              "denoise1x",
              "denoise2x",
              "denoise3x",
            ],
            3: ["conservative", "denoise3x"],
            4: ["conservative", "no-denoise", "denoise3x"],
          },
          tile_size: [32, 48, 64, 128],
        },
      },
      model: "anime_plus",
      factor: 4,
      denoise: "conservative",
      tile_size: 64,
      min_lap: 12,
      save_quality: 92,
      backend: "webgl",
      info: "",
      worker: new Worker(new URL("./worker.js", import.meta.url), {
        type: "module",
      }),
      wasmModule: null,
    };
  },
  watch: {
    model() {
      localStorage.setItem("model", this.model);
    },
    backend() {
      localStorage.setItem("backend", this.backend);
    },
    factor() {
      localStorage.setItem("factor", this.factor);
      if (
        !this.model_config.realcugan.denoise[this.factor].includes(this.denoise)
      ) {
        this.denoise = this.model_config.realcugan.denoise[this.factor][0];
      }
    },
    denoise() {
      localStorage.setItem("denoise", this.denoise);
    },
    tile_size() {
      localStorage.setItem("tile_size", this.tile_size);
    },
    min_lap() {
      localStorage.setItem("min_lap", this.min_lap);
    },
    model_type() {
      if (this.model_type === "realesrgan") {
        if (!this.model_config.realesrgan.model.includes(this.model)) {
          this.model = "anime_plus";
        }
        this.factor = 4;
        this.tile_size = 64;
      } else {
      }
    },
  },
  computed: {
    menu_style() {
      if (this.imgLoaded) {
        if (this.isProcessing || this.isDone) {
          return {
            height: "60px",
          };
        }
        return {
          opacity: 1,
        };
      } else {
        return {
          opacity: 0,
          height: "150px",
          transition: "all 0s ease",
        };
      }
    },
    upload_button_style() {
      if (this.isDragOver) {
        return {
          width: "256px",
          height: "256px",
          "background-color": "pink",
        };
      }
    },
  },
  mounted() {
    this.model_type = localStorage.getItem("model_type") || "realcugan";
    this.model = localStorage.getItem("model") || "anime_plus";
    this.factor = Number(localStorage.getItem("factor")) || 4;
    this.denoise = localStorage.getItem("denoise") || "conservative";
    this.tile_size = Number(localStorage.getItem("tile_size")) || 64;
    this.min_lap = Number(localStorage.getItem("min_lap")) || 12;
    this.backend = localStorage.getItem("backend") || "webgl";
    window.addEventListener("resize", this.handleResize);
    this.initializeCanvas();
    this.linePosition = this.$refs.canvas.width * 2;
    this.$refs.dragLine.style.left = this.linePosition / this.dpr + "px";
    (async () => {
      await Module();
    })();
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    initializeCanvas() {
      this.updateCanvasSize();
    },
    updateCanvasSize() {
      const container = this.$refs.canvasContainer;
      const canvas = this.$refs.canvas;
      if (this.imgLoaded) {
        this.imgX =
          ((this.imgX + (this.img.width * this.imgScale) / 2) / canvas.width) *
            container.offsetWidth *
            this.dpr -
          (this.img.width * this.imgScale) / 2;
        this.imgY =
          ((this.imgY + (this.img.height * this.imgScale) / 2) /
            canvas.height) *
            container.offsetHeight *
            this.dpr -
          (this.img.height * this.imgScale) / 2;
        this.linePosition =
          (this.linePosition / canvas.width) * container.offsetWidth * this.dpr;
        this.$refs.dragLine.style.left = this.linePosition / this.dpr + "px";
      }
      canvas.width = container.offsetWidth * this.dpr;
      canvas.height = container.offsetHeight * this.dpr;
      canvas.style.width = `${container.offsetWidth}px`;
      canvas.style.height = `${container.offsetHeight}px`;
      this.drawImage();
    },
    handleResize() {
      this.updateCanvasSize();
    },
    loadImg(src) {
      this.img.src = src;
      this.img.onload = async () => {
        this.imgLoaded = true;
        this.drawLine = true;

        let wasmModule = await Module();
        this.wasmModule = wasmModule;
        const imgCanvas = this.$refs.imgCanvas;
        imgCanvas.width = this.img.width;
        imgCanvas.height = this.img.height;
        const imgCtx = imgCanvas.getContext("2d");
        imgCtx.drawImage(this.img, 0, 0);
        let data = imgCtx.getImageData(
          0,
          0,
          this.img.width,
          this.img.height
        ).data;
        this.input = new Img(this.img.width, this.img.height, data);
        const numPixels = this.input.width * this.input.height;
        const bytesPerImage = numPixels * 4;
        let sourcePtr = wasmModule._malloc(bytesPerImage);
        let targetPtr = wasmModule._malloc(bytesPerImage);
        wasmModule.HEAPU8.set(this.input.data, sourcePtr);
        this.hasAlpha = wasmModule._check_alpha(sourcePtr, numPixels);
        if (this.hasAlpha) {
          this.inputAlpha = new Img(this.img.width, this.img.height);
          wasmModule._copy_alpha_to_rgb(sourcePtr, targetPtr, numPixels);
          this.inputAlpha.data.set(
            wasmModule.HEAPU8.subarray(targetPtr, targetPtr + bytesPerImage)
          );
        }
        wasmModule._free(sourcePtr);
        wasmModule._free(targetPtr);

        const canvas = this.$refs.canvas;
        const containerWidth = canvas.width;
        const containerHeight = canvas.height;

        const scaleX = (0.8 * containerWidth) / this.img.width;
        const scaleY = (0.8 * containerHeight) / this.img.height;
        this.imgScale = Math.min(scaleX, scaleY, 4);
        this.imgInitScale = this.imgScale;

        this.imgX = (containerWidth - this.img.width * this.imgScale) / 2;
        this.imgY = (containerHeight - this.img.height * this.imgScale) * 0.4;

        this.drawImage();
      };
    },
    testdemo(event) {
      const img = event.target;
      this.loadImg(img.src);
    },
    handleDrop(event) {
      if (this.imgLoaded) {
        event.preventDefault();
        return;
      }
      const files = event.dataTransfer.files;
      if (files && files.length > 0) {
        const file = files[0];
        this.imgName = file.name
          .replace(".jpg", "")
          .replace(".jpeg", "")
          .replace(".png", "");
        const reader = new FileReader();
        reader.onload = (e) => {
          this.loadImg(e.target.result);
        };
        reader.readAsDataURL(file);
      }
    },
    handleClick() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.onchange = (e) => {
        const file = e.target.files[0];
        this.imgName = file.name
          .replace(".jpg", "")
          .replace(".jpeg", "")
          .replace(".png", "");
        const reader = new FileReader();
        reader.onload = (e) => {
          this.loadImg(e.target.result);
        };
        reader.readAsDataURL(file);
      };
      input.click();
    },
    drawImage() {
      requestAnimationFrame(() => this.drawImage_());
      // this.drawImage_();
    },
    drawImage_() {
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.drawImage(
        this.img,
        this.imgX,
        this.imgY,
        this.img.width * this.imgScale,
        this.img.height * this.imgScale
      );

      if (this.processedImg.src) {
        ctx.drawImage(
          this.processedImg,
          ((this.processedImg.width / this.img.width) *
            (this.linePosition - this.imgX)) /
            this.imgScale,
          0,
          this.processedImg.width -
            ((this.processedImg.width / this.img.width) *
              (this.linePosition - this.imgX)) /
              this.imgScale,
          this.processedImg.height,
          this.linePosition,
          this.imgY,
          this.imgX + this.img.width * this.imgScale - this.linePosition,
          this.img.height * this.imgScale
        );
      }
    },
    startDragging(event) {
      if (!this.imgLoaded) return;
      const rect = this.$refs.canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      if (Math.abs(mouseX - this.linePosition / this.dpr) < 12) {
        this.startDraggingLine(event);
        return;
      }
      this.dragging = true;
    },
    stopDragging() {
      if (!this.imgLoaded) return;
      if (this.draggingLine) {
        this.stopDraggingLine();
        return;
      }
      this.dragging = false;
    },
    dragImage(event) {
      if (this.dragging) {
        this.imgX += event.movementX * this.dpr;
        this.imgY += event.movementY * this.dpr;
        this.drawImage();
      }
      if (this.draggingLine) {
        this.updateLinePosition(event);
        this.drawImage();
      }
    },
    touchDragImage(event) {
      if (this.touching) {
        const touch = event.touches[0];
        this.imgX += touch.clientX - this.touchStartX;
        this.imgY += touch.clientY - this.touchStartY;
        this.drawImage();
      }
      if (this.draggingLine) {
        this.updateLinePosition(event);
        this.drawImage();
      }
    },
    resizeImage(event) {
      if (!this.imgLoaded) return;
      event.preventDefault();
      const canvas = this.$refs.canvas;
      const rect = canvas.getBoundingClientRect();
      const mouseX = (event.clientX - rect.left) * this.dpr;
      const mouseY = (event.clientY - rect.top) * this.dpr;
      const prevScale = this.imgScale;
      const maxSize = 20 * this.imgInitScale;
      const minSize = 0.05 * this.imgInitScale;
      if (event.deltaY > 0) {
        const newScale = this.imgScale * 0.8;
        this.imgScale = Math.min(Math.max(minSize, newScale), maxSize);
      } else {
        const newScale = this.imgScale * 1.2;
        this.imgScale = Math.min(Math.max(minSize, newScale), maxSize);
      }

      const scaleRatio = this.imgScale / prevScale;
      this.imgX = mouseX - (mouseX - this.imgX) * scaleRatio;
      this.imgY = mouseY - (mouseY - this.imgY) * scaleRatio;

      this.drawImage();
    },
    touchStart(event) {
      this.touching = true;
      this.touchStartImgX = this.imgX;
      this.touchStartImgY = this.imgY;
      if (event.touches.length == 1) {
        if (
          Math.abs(event.touches[0].clientX - this.linePosition / this.dpr) < 12
        ) {
          this.draggingLine = true;
          return;
        }
        this.touchStartX = event.touches[0].clientX * this.dpr;
        this.touchStartY = event.touches[0].clientY * this.dpr;
      } else {
        this.imgScaleStart = this.imgScale;
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        this.touchStartDistance =
          Math.sqrt(
            Math.pow(touch2.clientX - touch1.clientX, 2) +
              Math.pow(touch2.clientY - touch1.clientY, 2)
          ) * this.dpr;
        this.touchStartX = ((touch1.clientX + touch2.clientX) / 2) * this.dpr;
        this.touchStartY = ((touch1.clientY + touch2.clientY) / 2) * this.dpr;
      }
    },
    touchMove(event) {
      event.preventDefault();
      if (!this.touching) {
        return;
      }
      if (event.touches.length == 1) {
        const touch = event.touches[0];
        const movementX =
          touch.clientX * this.dpr -
          this.touchStartX +
          this.touchStartImgX -
          this.imgX;
        const movementY =
          touch.clientY * this.dpr -
          this.touchStartY +
          this.touchStartImgY -
          this.imgY;
        if (this.draggingLine) {
          this.updateLinePosition(event.touches[0]);
          this.drawImage();
          return;
        }
        if (this.touching) {
          this.imgX += movementX;
          this.imgY += movementY;
          this.drawImage();
        }
      } else {
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        const distance =
          Math.sqrt(
            Math.pow(touch2.clientX - touch1.clientX, 2) +
              Math.pow(touch2.clientY - touch1.clientY, 2)
          ) * this.dpr;
        const canvas = this.$refs.canvas;
        const rect = canvas.getBoundingClientRect();
        const mouseX = this.touchStartX - rect.left;
        const mouseY = this.touchStartY - rect.top;
        const scaleChange = distance / this.touchStartDistance;
        const prevScale = this.imgScale;
        const maxSize = 20 * this.imgInitScale;
        const minSize = 0.05 * this.imgInitScale;
        const newScale = this.imgScaleStart * scaleChange;
        this.imgScale = Math.min(Math.max(minSize, newScale), maxSize);

        const scaleRatio = this.imgScale / prevScale;
        const movementX =
          ((touch1.clientX + touch2.clientX) / 2) * this.dpr - this.touchStartX;
        const movementY =
          ((touch1.clientY + touch2.clientY) / 2) * this.dpr - this.touchStartY;
        this.imgX = mouseX - (mouseX - this.imgX) * scaleRatio + movementX;
        this.imgY = mouseY - (mouseY - this.imgY) * scaleRatio + movementY;
        this.touchStartX = ((touch1.clientX + touch2.clientX) / 2) * this.dpr;
        this.touchStartY = ((touch1.clientY + touch2.clientY) / 2) * this.dpr;
        this.drawImage();
      }
    },
    touchEnd(event) {
      if (event.touches.length == 2) {
        this.touchStartImgX = this.imgX;
        this.touchStartImgY = this.imgY;
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        this.touchStartDistance =
          Math.sqrt(
            Math.pow(touch2.clientX - touch1.clientX, 2) +
              Math.pow(touch2.clientY - touch1.clientY, 2)
          ) * this.dpr;
        this.touchStartX = ((touch1.clientX + touch2.clientX) / 2) * this.dpr;
        this.touchStartY = ((touch1.clientY + touch2.clientY) / 2) * this.dpr;
        return;
      }
      if (event.touches.length == 1) {
        this.touchStartImgX = this.imgX;
        this.touchStartImgY = this.imgY;
        this.touchStartX = event.touches[0].clientX * this.dpr;
        this.touchStartY = event.touches[0].clientY * this.dpr;
        return;
      }
      this.touching = false;
      this.draggingLine = false;
      this.touchStartImgX = null;
      this.touchStartImgY = null;
      this.touchStartX = null;
      this.touchStartY = null;
      this.touchStartDistance = null;
    },
    startDraggingLine(event) {
      event.preventDefault();
      if (!this.isDone) return;
      this.draggingLine = true;
    },
    stopDraggingLine() {
      this.draggingLine = false;
    },
    dragLine(event) {
      event.preventDefault();
      if (this.draggingLine) {
        this.updateLinePosition(event);
        this.drawImage();
      }
    },
    updateLinePosition(event) {
      const rect = this.$refs.canvas.getBoundingClientRect();
      this.linePosition = event.clientX * this.dpr - rect.left;
      const line = this.$refs.dragLine;
      line.style.left = Math.floor(this.linePosition / this.dpr) + "px";
    },
    startTask() {
      if (this.input === null) return;
      this.isProcessing = true;
      let worker = this.worker;
      let start = Date.now();
      worker.addEventListener("message", (e) => {
        const { progress, done, output, alertmsg, info } = e.data;
        if (info) {
          this.info = info;
        }
        if (alertmsg) {
          alert(alertmsg);
          this.isProcessing = false;
          worker.terminate();
          return;
        }
        this.progress = progress;
        if (done) {
          if (!this.hasAlpha || (this.hasAlpha && this.inputAlpha)) {
            let factor = this.factor;
            this.output = new Img(
              factor * this.input.width,
              factor * this.input.height,
              new Uint8ClampedArray(output)
            );
          }
          this.info = "Processing Image...";
          if (this.inputAlpha) {
            worker.postMessage(
              {
                input: this.inputAlpha.data.buffer,
                factor: this.factor,
                denoise: this.denoise,
                tile_size: this.tile_size,
                min_lap: this.min_lap,
                model_type: this.model_type,
                width: this.inputAlpha.width,
                height: this.inputAlpha.height,
                model: this.model,
                backend: this.backend,
                hasAlpha: true,
              },
              [this.inputAlpha.data.buffer]
            );
            this.inputAlpha = null;
            return;
          }
          if (this.hasAlpha) {
            let outputArray = new Uint8Array(output);
            let wasmModule = this.wasmModule;
            let sourcePtr = wasmModule._malloc(outputArray.length);
            let targetPtr = wasmModule._malloc(outputArray.length);
            let numPixels = outputArray.length / 4;
            wasmModule.HEAPU8.set(outputArray, sourcePtr);
            wasmModule.HEAPU8.set(this.output.data, targetPtr);
            wasmModule._copy_alpha_channel(sourcePtr, targetPtr, numPixels);
            this.output.data.set(
              wasmModule.HEAPU8.subarray(
                targetPtr,
                targetPtr + outputArray.length
              )
            );
            wasmModule._free(sourcePtr);
            wasmModule._free(targetPtr);
            wasmModule = null;
            this.wasmModule = null;
          }

          const imgCanvas = this.$refs.imgCanvas;
          const imgCtx = imgCanvas.getContext("2d");
          imgCtx.clearRect(0, 0, imgCanvas.width, imgCanvas.height);
          imgCanvas.width = this.output.width;
          imgCanvas.height = this.output.height;
          let outImg = imgCtx.createImageData(
            this.output.width,
            this.output.height
          );
          outImg.data.set(this.output.data);
          this.input = null;
          this.inputAlpha = null;
          this.output = null;
          imgCtx.putImageData(outImg, 0, 0);
          let type = "image/jpeg";
          let quality = 0.92;
          if (this.hasAlpha) type = "image/png";
          imgCanvas.toBlob(
            (blob) => {
              this.processedImg.src = URL.createObjectURL(blob);
            },
            type,
            quality
          );
          this.processedImg.onload = () => {
            this.linePosition = this.$refs.canvas.width * 0.5;
            this.$refs.dragLine.style.left =
              this.linePosition / this.dpr + "px";
            this.drawImage();
            this.info = "Done! Time used: " + (Date.now() - start) / 1000 + "s";
          };
          this.isProcessing = false;
          this.isDone = true;
          worker.terminate();
        }
      });
      worker.postMessage(
        {
          input: this.input.data.buffer,
          factor: this.factor,
          denoise: this.denoise,
          tile_size: this.tile_size,
          min_lap: this.min_lap,
          model_type: this.model_type,
          width: this.input.width,
          height: this.input.height,
          model: this.model,
          backend: this.backend,
          hasAlpha: false,
        },
        [this.input.data.buffer]
      );
    },
    saveImage() {
      const a = document.createElement("a");
      a.href = this.processedImg.src;
      if (this.hasAlpha) a.download = this.imgName + ".png";
      else a.download = this.imgName + ".jpg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    reloadPage() {
      this.worker.terminate();
      this.worker = new Worker(new URL("./worker.js", import.meta.url), {
        type: "module",
      });
      //reset
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      this.dragging = false;
      this.touching = false;
      this.imgX = 0;
      this.imgY = 0;
      this.imgScale = 1;
      this.imgInitScale = 1;
      this.linePosition = 0;
      this.drawLine = false;
      this.draggingLine = false;
      this.imgLoaded = false;
      this.dpr = window.devicePixelRatio || 1;
      this.img = new Image();
      this.processedImg = new Image();
      this.hasAlpha = false;
      this.touchStartImgX = null;
      this.touchStartImgY = null;
      this.touchStartX = null;
      this.touchStartY = null;
      this.touchStartDistance = null;
      this.imgScaleStart = 1;

      this.imgLoaded = false;
      this.input = null;
      this.inputAlpha = null;
      this.output = null;
      this.isDragOver = false;
      this.isProcessing = false;
      this.isDone = false;
      this.progress = 0;
      this.model = localStorage.getItem("model") || "anime_plus";
      this.backend = localStorage.getItem("backend") || "webgl";
      this.info = "";
    },
  },
};
</script>
