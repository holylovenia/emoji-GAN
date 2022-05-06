import imageio
import os
import torch
import scipy
import scipy.misc
import numpy as np
from models import CycleGenerator, DCDiscriminator

SEED = 11

# Set the random seed manually for reproducibility.
torch.manual_seed(SEED)

def create_dir(directory):
    """Creates a directory if it does not already exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_model(opts):
    """Builds the generators and discriminators.
    """
    G_XtoY = CycleGenerator(conv_dim=opts.g_conv_dim, init_zero_weights=opts.init_zero_weights)
    G_YtoX = CycleGenerator(conv_dim=opts.g_conv_dim, init_zero_weights=opts.init_zero_weights)
    D_X = DCDiscriminator(conv_dim=opts.d_conv_dim)
    D_Y = DCDiscriminator(conv_dim=opts.d_conv_dim)

    return G_XtoY, G_YtoX, D_X, D_Y


def checkpoint(iteration, G_XtoY, G_YtoX, D_X, D_Y, opts):
    """Saves the parameters of both generators G_YtoX, G_XtoY and discriminators D_X, D_Y.
    """
    ckpt_path = os.path.join(opts.checkpoint_dir, 'ckpt_{:06d}.pth.tar'.format(iteration))
    torch.save({'G_XtoY': G_XtoY.state_dict(),
                'G_YtoX': G_YtoX.state_dict(),
                'D_X': D_X.state_dict(),
                'D_Y': D_Y.state_dict(),
                'iter': iteration}, 
               ckpt_path)


def merge_images(sources, targets, opts, k=10):
    """Creates a grid consisting of pairs of columns, where the first column in
    each pair contains images source images and the second column in each pair
    contains images generated by the CycleGAN from the corresponding images in
    the first column.
    """
    _, _, h, w = sources.shape
    row = int(np.sqrt(opts.batch_size))
    merged = np.zeros([3, row*h, row*w*2])
    for idx, (s, t) in enumerate(zip(sources, targets)):
        i = idx // row
        j = idx % row
        merged[:, i*h:(i+1)*h, (j*2)*h:(j*2+1)*h] = s
        merged[:, i*h:(i+1)*h, (j*2+1)*h:(j*2+2)*h] = t
    return merged.transpose(1, 2, 0)


def save_samples(iteration, fixed_Y, fixed_X, G_YtoX, G_XtoY, opts):
    """Saves samples from both generators X->Y and Y->X.
    """
    fake_X = G_YtoX(fixed_Y)
    fake_Y = G_XtoY(fixed_X)

    X, fake_X = fixed_X.cpu().data.numpy(), fake_X.cpu().data.numpy()
    Y, fake_Y = fixed_Y.cpu().data.numpy(), fake_Y.cpu().data.numpy()

    merged = merge_images(X, fake_Y, opts)
    path = os.path.join(opts.sample_dir, 'sample-{:06d}-X-Y.png'.format(iteration))
    imageio.imwrite(path, merged)
    print('Saved {}'.format(path))

    merged = merge_images(Y, fake_X, opts)
    path = os.path.join(opts.sample_dir, 'sample-{:06d}-Y-X.png'.format(iteration))
    imageio.imwrite(path, merged)
    print('Saved {}'.format(path))

