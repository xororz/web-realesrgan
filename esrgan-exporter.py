import os
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
import torch

model2name = {
    "realesr-animevideov3": "anime_fast",
    "RealESRGAN_x4plus_anime_6B": "anime_plus",
    "realesr-general-x4v3": "general_fast",
    "RealESRGAN_x4plus": "general_plus",
}


def export(model_name, tile_size):
    if model_name == "RealESRGAN_x4plus":  # x4 RRDBNet model
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )
        netscale = 4
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        ]
    elif model_name == "RealESRNet_x4plus":  # x4 RRDBNet model
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )
        netscale = 4
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth"
        ]
    elif model_name == "RealESRGAN_x4plus_anime_6B":  # x4 RRDBNet model with 6 blocks
        model = RRDBNet(
            num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4
        )
        netscale = 4
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
        ]
    elif model_name == "RealESRGAN_x2plus":  # x2 RRDBNet model
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=2,
        )
        netscale = 2
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth"
        ]
    elif model_name == "realesr-animevideov3":  # x4 VGG-style model (XS size)
        model = SRVGGNetCompact(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_conv=16,
            upscale=4,
            act_type="prelu",
        )
        netscale = 4
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth"
        ]
    elif model_name == "realesr-general-x4v3":  # x4 VGG-style model (S size)
        model = SRVGGNetCompact(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_conv=32,
            upscale=4,
            act_type="prelu",
        )
        netscale = 4
        file_url = [
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth",
            "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        ]

    model_path = os.path.join("weights", model_name + ".pth")
    if not os.path.isfile(model_path):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        for url in file_url:
            # model_path will be updated
            model_path = load_file_from_url(
                url=url,
                model_dir=os.path.join(ROOT_DIR, "weights"),
                progress=True,
                file_name=None,
            )

    # use dni to control the denoise strength
    dni_weight = None
    denoise_strength = 0.5
    if model_name == "realesr-general-x4v3" and denoise_strength != 1:
        wdn_model_path = model_path.replace(
            "realesr-general-x4v3", "realesr-general-wdn-x4v3"
        )
        model_path = [model_path, wdn_model_path]
        dni_weight = [denoise_strength, 1 - denoise_strength]

    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        dni_weight=dni_weight,
        model=model,
        tile=0,
        tile_pad=0,
        pre_pad=0,
        half=False,
        gpu_id=None,
    )

    name = model2name[model_name]
    torch.onnx.export(
        upsampler.model,
        torch.randn(1, 3, tile_size, tile_size),
        f"{name}.onnx",
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
    )
    os.system(f"onnxsim {name}.onnx {name}.onnx")
    os.system(
        f"onnx2tf -i {name}.onnx -osd -ois input:1,3,{tile_size},{tile_size} -o {name}-{tile_size}-tf"
    )
    # export tfjs_converter = xxx
    if not os.path.exists("tfjs"):
        os.mkdir("tfjs")
    os.system(
        # f"{os.environ['tfjs_converter']} --quantize_float16 --input_format tf_saved_model --output_format tfjs_graph_model {name}-{tile_size}-tf tfjs/{name}-{tile_size}"
        f"{os.environ['tfjs_converter']} --control_flow_v2=True --quantize_float16 --input_format tf_saved_model --output_format tfjs_graph_model {name}-{tile_size}-tf tfjs/{name}-{tile_size}"
    )


for model_name in model2name.keys():
    for tile_size in [32, 48, 64, 96, 128, 192, 256]:
        export(model_name, tile_size)
