"""Tests for conv relu module."""

import pytest
from pytest import approx
from . import torch_equal
from msd_pytorch.conv3d import (
    Conv3DReluInPlaceModule,
    conv3d_reluInPlace,
)
import torch
from torch.autograd import Variable
from torch.autograd import gradcheck
import torch.nn as nn
import msd_custom_convolutions as cc


def test_conv3d():
    """Test 3D custom convolution module

    We compare our custom reflection-padded convolution to the builtin
    Torch convolution.

    We check that:
    - The shape of the output is equal
    - The output values are equal in the center, where the
      reflection-padding should not have influenced the result.

    """

    batch_sz = 5
    c_in = 1
    c_out = 1
    kernel_size = 3
    padding_torch = 1
    size = (45, 55, 65)

    # xi: for inplace
    # xc: for normal torch convolution
    xi = torch.randn(batch_sz, c_in, *size).cuda()
    xc = xi.data.clone()

    xi.requires_grad = True
    xc.requires_grad = True

    output = torch.ones(batch_sz, c_out, *size).cuda()
    ci = Conv3DReluInPlaceModule(
        output, c_in, c_out, kernel_size=kernel_size
    )
    cc = nn.Sequential(
        nn.Conv3d(c_in, c_out, kernel_size=kernel_size, padding=padding_torch),
        nn.ReLU(),
    )

    for c in [ci, *cc.modules()]:
        c.cuda()
        try:
            c.weight.data.fill_(1)
            c.bias.data.zero_()
        except AttributeError:
            pass  # skip relu (it does not have parameters)

    yi = ci(xi)
    yc = cc(xc)
    assert yi.shape == yc.shape

    # Check center of output, where the output should be equal.
    d = 1
    yi_ = yi[:, :, d:-d, d:-d, d:-d]
    yc_ = yc[:, :, d:-d, d:-d, d:-d]

    # Check that pytorch and own convolution agree in the center:
    assert torch_equal(yi_, yc_)
    assert torch_equal(yi.data, output)


def test_dtype_check():
    """Test if dtype checks are performed correctly
    """
    d0 = torch.float
    d1 = torch.double
    dilation = 1

    x = torch.zeros(1, 1, 5, 5, 5, dtype=d0).cuda()
    y = torch.zeros(1, 1, 5, 5, 5, dtype=d0).cuda()
    bias = torch.zeros(1, dtype=d1).cuda()
    k = torch.zeros(1, 1, 3, 3, 3, dtype=d1).cuda()

    with pytest.raises(RuntimeError):
        cc.conv3d_relu_forward(x, k, bias, y, dilation)


def test_zero_conv():
    """Test convolution

    Check if an all-zero convolution runs without runtime errors.
    """
    dtype = torch.float  # or t.double
    dilation = 1

    x = torch.zeros(1, 1, 5, 5, 5, dtype=dtype).cuda()
    y = torch.ones(1, 1, 5, 5, 5, dtype=dtype).cuda()
    bias = torch.zeros(1, dtype=dtype).cuda()
    k = torch.zeros(1, 1, 3, 3, 3, dtype=dtype).cuda()

    cc.conv3d_relu_forward(x, k, bias, y, dilation)
    assert y.sum().item() == approx(0.0)


test_params = [
    (b, c_in, c_out, dil, size)
    for b in [2]
    for c_in in [3]
    for c_out in [5]
    for dil in [1, 3, 10]
    for size in [dil * 2 + 1, 29, 50]
]


@pytest.mark.parametrize(
    "B, C_in, C_out, dilation, size",
    test_params,
)
def test_conv_values(B, C_in, C_out, dilation, size):
    """Compare to pytorch convolution

    Check that the convolution agrees with a pytorch convolution
    on the output area that is not reflected.
    """
    dtype = torch.double

    shape = (size, 2 * size, 3 * size)

    # Execute my own implementation
    x = torch.randn(B, C_in, *shape, dtype=dtype).cuda()
    k = torch.randn(C_out, C_in, 3, 3, 3, dtype=dtype).cuda()
    bias = torch.randn(C_out, dtype=dtype).cuda()
    y = torch.zeros(B, C_out, *shape, dtype=dtype).cuda()
    cc.conv3d_relu_forward(x, k, bias, y, dilation)

    # Execute pytorch convolution:
    conv_torch = torch.nn.Conv3d(
        C_in, C_out, 3, padding=dilation, dilation=dilation
    ).cuda()
    conv_torch.weight.data = k
    conv_torch.bias.data = bias
    y1 = nn.ReLU()(conv_torch(x))

    # check shapes
    assert y1.shape == y.shape

    # Check center of output, where the output should be equal.
    d = dilation
    y_ = y[:, :, d:-d, d:-d, d:-d]
    y1_ = y1[:, :, d:-d, d:-d, d:-d]
    assert torch_equal(y1_, y_), (
        f"for shape {shape} and dilation {dilation} "
        f"and bias {bias}"
        f"\nYour implementation:\n{y}"
        f"\nPyTorch:\n{y1}"
    )


def test_grad_check():
    """Test using gradcheck provided by Torch.

    Because there is no reference implementation to compare to, we
    check if the gradient calculations are consistent with numerical
    calculations.

    """
    dtype = torch.double    # Extra machine precision is needed.
    B = 2                   # Batch size
    C_IN = 3                # Input channels
    C_OUT = 2               # Output channels
    D = 11                  # Depth
    H = 13                  # Height
    W = 21                  # Width
    dilation = 3            # Dilation

    x = torch.randn(B, C_IN, D, H, W, dtype=dtype, requires_grad=True).cuda()
    k = torch.randn(C_OUT, C_IN, 3, 3, 3, dtype=dtype, requires_grad=True).cuda()
    b = torch.randn(C_OUT, dtype=dtype, requires_grad=True).cuda()

    def f(x, k, b, dilation):
        output_shape = list(x.shape)
        output_shape[1] = k.shape[0]
        output = x.new_zeros(output_shape, requires_grad=True)
        stride = 1
        return conv3d_reluInPlace(x, k, b, output, stride, dilation)

    gradcheck(f, [x, k, b, dilation], raise_exception=True)
