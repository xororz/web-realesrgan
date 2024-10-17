import torch
from torch import nn as nn
from torch.nn import functional as F
import os, sys
import numpy as np

root_path = os.path.abspath(".")
sys.path.append(root_path)


def q(inp, cache_mode):
    maxx = inp.max()
    minn = inp.min()
    delta = maxx - minn
    if cache_mode == 2:
        return (
            ((inp - minn) / delta * 255).round().byte().cpu(),
            delta,
            minn,
            inp.device,
        )
    elif cache_mode == 1:
        return (
            ((inp - minn) / delta * 255).round().byte(),
            delta,
            minn,
            inp.device,
        )


def dq(inp, if_half, cache_mode, delta, minn, device):
    if cache_mode == 2:
        if if_half == True:
            return inp.to(device).half() / 255 * delta + minn
        else:
            return inp.to(device).float() / 255 * delta + minn
    elif cache_mode == 1:
        if if_half == True:
            return inp.half() / 255 * delta + minn
        else:
            return inp.float() / 255 * delta + minn


class SEBlock(nn.Module):
    def __init__(self, in_channels, reduction=8, bias=False):
        super(SEBlock, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels, in_channels // reduction, 1, 1, 0, bias=bias
        )
        self.conv2 = nn.Conv2d(
            in_channels // reduction, in_channels, 1, 1, 0, bias=bias
        )

    def forward(self, x):
        if "Half" in x.type():
            x0 = torch.mean(x.float(), dim=(2, 3), keepdim=True).half()
        else:
            x0 = torch.mean(x, dim=(2, 3), keepdim=True)
        x0 = self.conv1(x0)
        x0 = F.relu(x0, inplace=True)
        x0 = self.conv2(x0)
        x0 = torch.sigmoid(x0)
        x = torch.mul(x, x0)
        return x

    def forward_mean(self, x, x0):
        x0 = self.conv1(x0)
        x0 = F.relu(x0, inplace=True)
        x0 = self.conv2(x0)
        x0 = torch.sigmoid(x0)
        x = torch.mul(x, x0)
        return x


class UNetConv(nn.Module):
    def __init__(self, in_channels, mid_channels, out_channels, se):
        super(UNetConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, 3, 1, 0),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(mid_channels, out_channels, 3, 1, 0),
            nn.LeakyReLU(0.1, inplace=True),
        )
        if se:
            self.seblock = SEBlock(out_channels, reduction=8, bias=True)
        else:
            self.seblock = None

    def forward(self, x):
        z = self.conv(x)
        if self.seblock is not None:
            z = self.seblock(z)
        return z


class UNet1(nn.Module):
    def __init__(self, in_channels, out_channels, deconv):
        super(UNet1, self).__init__()
        self.conv1 = UNetConv(in_channels, 32, 64, se=False)
        self.conv1_down = nn.Conv2d(64, 64, 2, 2, 0)
        self.conv2 = UNetConv(64, 128, 64, se=True)
        self.conv2_up = nn.ConvTranspose2d(64, 64, 2, 2, 0)
        self.conv3 = nn.Conv2d(64, 64, 3, 1, 0)

        if deconv:
            self.conv_bottom = nn.ConvTranspose2d(64, out_channels, 4, 2, 3)
        else:
            self.conv_bottom = nn.Conv2d(64, out_channels, 3, 1, 0)

        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-4, -4, -4, -4))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2(x2)
        x2 = self.conv2_up(x2)
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x3 = self.conv3(x1 + x2)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        z = self.conv_bottom(x3)
        return z

    def forward_a(self, x):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-4, -4, -4, -4))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2.conv(x2)
        return x1, x2

    def forward_b(self, x1, x2):
        x2 = self.conv2_up(x2)
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x3 = self.conv3(x1 + x2)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        z = self.conv_bottom(x3)
        return z


class UNet1x3(nn.Module):
    def __init__(self, in_channels, out_channels, deconv):
        super(UNet1x3, self).__init__()
        self.conv1 = UNetConv(in_channels, 32, 64, se=False)
        self.conv1_down = nn.Conv2d(64, 64, 2, 2, 0)
        self.conv2 = UNetConv(64, 128, 64, se=True)
        self.conv2_up = nn.ConvTranspose2d(64, 64, 2, 2, 0)
        self.conv3 = nn.Conv2d(64, 64, 3, 1, 0)

        if deconv:
            self.conv_bottom = nn.ConvTranspose2d(64, out_channels, 5, 3, 2)
        else:
            self.conv_bottom = nn.Conv2d(64, out_channels, 3, 1, 0)

        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-4, -4, -4, -4))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2(x2)
        x2 = self.conv2_up(x2)
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x3 = self.conv3(x1 + x2)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        z = self.conv_bottom(x3)
        return z

    def forward_a(self, x):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-4, -4, -4, -4))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2.conv(x2)
        return x1, x2

    def forward_b(self, x1, x2):
        x2 = self.conv2_up(x2)
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x3 = self.conv3(x1 + x2)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        z = self.conv_bottom(x3)
        return z


class UNet2(nn.Module):
    def __init__(self, in_channels, out_channels, deconv):
        super(UNet2, self).__init__()

        self.conv1 = UNetConv(in_channels, 32, 64, se=False)
        self.conv1_down = nn.Conv2d(64, 64, 2, 2, 0)
        self.conv2 = UNetConv(64, 64, 128, se=True)
        self.conv2_down = nn.Conv2d(128, 128, 2, 2, 0)
        self.conv3 = UNetConv(128, 256, 128, se=True)
        self.conv3_up = nn.ConvTranspose2d(128, 128, 2, 2, 0)
        self.conv4 = UNetConv(128, 64, 64, se=True)
        self.conv4_up = nn.ConvTranspose2d(64, 64, 2, 2, 0)
        self.conv5 = nn.Conv2d(64, 64, 3, 1, 0)

        if deconv:
            self.conv_bottom = nn.ConvTranspose2d(64, out_channels, 4, 2, 3)
        else:
            self.conv_bottom = nn.Conv2d(64, out_channels, 3, 1, 0)

        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x, alpha=1):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-16, -16, -16, -16))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2(x2)
        x3 = self.conv2_down(x2)
        x2 = F.pad(x2, (-4, -4, -4, -4))
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        x3 = self.conv3(x3)
        x3 = self.conv3_up(x3)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        x4 = self.conv4(x2 + x3)
        x4 *= alpha
        x4 = self.conv4_up(x4)
        x4 = F.leaky_relu(x4, 0.1, inplace=True)
        x5 = self.conv5(x1 + x4)
        x5 = F.leaky_relu(x5, 0.1, inplace=True)
        z = self.conv_bottom(x5)
        return z

    def forward_a(self, x):
        x1 = self.conv1(x)
        x2 = self.conv1_down(x1)
        x1 = F.pad(x1, (-16, -16, -16, -16))
        x2 = F.leaky_relu(x2, 0.1, inplace=True)
        x2 = self.conv2.conv(x2)
        return x1, x2

    def forward_b(self, x2):
        x3 = self.conv2_down(x2)
        x2 = F.pad(x2, (-4, -4, -4, -4))
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        x3 = self.conv3.conv(x3)
        return x2, x3

    def forward_c(self, x2, x3):
        x3 = self.conv3_up(x3)
        x3 = F.leaky_relu(x3, 0.1, inplace=True)
        x4 = self.conv4.conv(x2 + x3)
        return x4

    def forward_d(self, x1, x4):
        x4 = self.conv4_up(x4)
        x4 = F.leaky_relu(x4, 0.1, inplace=True)
        x5 = self.conv5(x1 + x4)
        x5 = F.leaky_relu(x5, 0.1, inplace=True)

        z = self.conv_bottom(x5)
        return z


class UpCunet2x(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super(UpCunet2x, self).__init__()
        self.unet1 = UNet1(in_channels, out_channels, deconv=True)
        self.unet2 = UNet2(in_channels, out_channels, deconv=False)

    def forward(self, x):
        x = F.pad(x, (18, 18, 18, 18), "reflect")
        x = self.unet1(x)
        x0 = self.unet2(x, 1)
        x = F.pad(x, (-20, -20, -20, -20))
        x = torch.add(x0, x)
        return x


class UpCunet3x(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super(UpCunet3x, self).__init__()
        self.unet1 = UNet1x3(in_channels, out_channels, deconv=True)
        self.unet2 = UNet2(in_channels, out_channels, deconv=False)

    def forward(self, x):
        x = F.pad(x, (14, 14, 14, 14), "reflect")
        x = self.unet1(x)
        x0 = self.unet2(x, 1)
        x = F.pad(x, (-20, -20, -20, -20))
        x = torch.add(x0, x)
        return x


class UpCunet4x(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super(UpCunet4x, self).__init__()
        self.unet1 = UNet1(in_channels, 64, deconv=True)
        self.unet2 = UNet2(64, 64, deconv=False)
        self.ps = nn.PixelShuffle(2)
        self.conv_final = nn.Conv2d(64, 12, 3, 1, padding=0, bias=True)

    def forward(self, x):
        x00 = x
        x = F.pad(x, (19, 19, 19, 19), "reflect")
        x = self.unet1.forward(x)
        x0 = self.unet2.forward(x, 1)
        x1 = F.pad(x, (-20, -20, -20, -20))
        x = torch.add(x0, x1)
        x = self.conv_final(x)
        x = F.pad(x, (-1, -1, -1, -1))
        x = self.ps(x)
        x += F.interpolate(x00, scale_factor=4, mode="nearest")
        return x


class RealWaifuUpScaler(object):
    def __init__(self, scale, weight_path, half, device):
        weight = torch.load(weight_path, map_location="cpu")
        self.pro = "pro" in weight
        if self.pro:
            del weight["pro"]
        self.model = eval("UpCunet%sx" % scale)()

        if half == True:
            self.model = self.model.half().to(device)
        else:
            self.model = self.model.to(device)
        self.model.load_state_dict(weight, strict=False)
        self.model.eval()
        self.half = half
        self.device = device

    def np2tensor(self, np_frame):
        if self.pro:
            if self.half == False:
                return (
                    torch.from_numpy(np.transpose(np_frame, (2, 0, 1)))
                    .unsqueeze(0)
                    .to(self.device)
                    .float()
                    / (255 / 0.7)
                    + 0.15
                )
            else:
                return (
                    torch.from_numpy(np.transpose(np_frame, (2, 0, 1)))
                    .unsqueeze(0)
                    .to(self.device)
                    .half()
                    / (255 / 0.7)
                    + 0.15
                )
        else:
            if self.half == False:
                return (
                    torch.from_numpy(np.transpose(np_frame, (2, 0, 1)))
                    .unsqueeze(0)
                    .to(self.device)
                    .float()
                    / 255
                )
            else:
                return (
                    torch.from_numpy(np.transpose(np_frame, (2, 0, 1)))
                    .unsqueeze(0)
                    .to(self.device)
                    .half()
                    / 255
                )

    def tensor2np(self, tensor):
        return np.transpose(tensor.squeeze().cpu().numpy(), (1, 2, 0))

    def __call__(self, frame, tile_mode, cache_mode, alpha):
        with torch.no_grad():
            tensor = self.np2tensor(frame)
            if cache_mode == 3:
                result = self.tensor2np(
                    self.model.forward_gap_sync(tensor, tile_mode, alpha, self.pro)
                )
            elif cache_mode == 2:
                result = self.tensor2np(
                    self.model.forward_fast_rough(tensor, tile_mode, alpha, self.pro)
                )
            else:
                result = self.tensor2np(self.model(tensor))
        return result


if __name__ == "__main__":
    for weight_path, scale, name in [
        ("./weights_v3/up2x-latest-conservative.pth", 2, "2x-conservative"),
        ("./weights_v3/up2x-latest-denoise1x.pth", 2, "2x-denoise1x"),
        ("./weights_v3/up2x-latest-denoise2x.pth", 2, "2x-denoise2x"),
        ("./weights_v3/up2x-latest-denoise3x.pth", 2, "2x-denoise3x"),
        ("./weights_v3/up2x-latest-no-denoise.pth", 2, "2x-no-denoise"),
        ("./weights_v3/up3x-latest-conservative.pth", 3, "3x-conservative"),
        ("./weights_v3/up3x-latest-denoise3x.pth", 3, "3x-denoise3x"),
        # ("./weights_v3/up3x-latest-no-denoise.pth", 3, "3x-no-denoise"), # error
        ("./weights_v3/up4x-latest-conservative.pth", 4, "4x-conservative"),
        ("./weights_v3/up4x-latest-denoise3x.pth", 4, "4x-denoise3x"),
        ("./weights_v3/up4x-latest-no-denoise.pth", 4, "4x-no-denoise"),
    ]:
        upscaler = RealWaifuUpScaler(scale, weight_path, half=False, device="cpu")
        # for tile_size in (64, 128):
        # for tile_size in (32, 48):
        # for tile_size in (32, 48, 64, 128):
        # for tile_size in (96,):
        # for tile_size in (192, 256):
        for tile_size in (384, 512):
            torch.onnx.export(
                upscaler.model,
                torch.randn(1, 3, tile_size, tile_size),
                f"{name}.onnx",
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=["input"],
                output_names=["output"],
                dynamic_axes={
                    "input": {2: "height", 3: "width"},
                    "output": {2: "height", 3: "width"},
                },
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
