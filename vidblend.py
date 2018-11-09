#! /usr/bin/env python
import os
import cv2
import argparse
import numpy as np
import progressbar

# OpenCV version must be >= 3.1
from distutils.version import StrictVersion
try:
  opencv_version = cv2.__version__.replace('-dev', '')
  if StrictVersion(opencv_version) < StrictVersion('3.1'):
    raise ImportError
except (AttributeError, ImportError):
  msg  = 'You need OpenCV >= 3.1. In Ubuntu 16.04 you can install it alongside ROS:'
  msg += '\tsudo apt install ros-kinetic-opencv3'
  raise ImportError(msg)


def restricted_factor(x):
  min_value = 0.01
  max_malue = 1.0
  x = float(x)
  if x < min_value or x > max_malue:
      raise argparse.ArgumentTypeError("{0} not in range [{1}, {2}]".format(x, min_value, max_malue))
  return x


if '__main__' == __name__:
  # Parse the args
  parser = argparse.ArgumentParser(
                formatter_class=argparse.RawDescriptionHelpFormatter,
                description='Video blender for moving objects on a static background',
                fromfile_prefix_chars='@')
  parser.add_argument('input', type=str, help='Path to the input video')
  parser.add_argument('--info', action='store_true',
                help='If set, ONLY shows the input video information')
  vis_group = parser.add_argument_group('visualization')
  vis_group.add_argument('--visualize', action='store_true',
                help='If set, visualize ONLY the process. ESC to quit')
  vis_group.add_argument('--vis-fps', metavar='', type=int, default=30,
                help='The FPS for the visualization. default=%(default)d')
  bld_group = parser.add_argument_group('blending')
  bld_group.add_argument('--alpha', metavar='', type=float, default=0.1,
                help='Blending transparency. default=%(default).2f')
  bld_group.add_argument('--sampling-factor', metavar='', type=restricted_factor, default=0.25,
                help='Percentage of frames to be used. default=%(default).2f')
  ft_group = parser.add_argument_group('filtering')
  ft_group.add_argument('--median-ksize', metavar='', type=int, default=3,
                help='Kernel size for the median noise filter. default=%(default)d')
  ft_group.add_argument('--morph-open-ksize', metavar='', type=int, default=11,
                help='Kernel size for open morphologic operation. default=%(default)d')
  cg_group = parser.add_argument_group('clustering')
  ft_group.add_argument('--min-targetobj-area', metavar='', type=int, default=5000,
                help='Min area to consider a countour to be the targetobj. default=%(default)d')
  ft_group.add_argument('--max-targetobj-area', metavar='', type=int, default=105000,
                help='Max area to consider a countour to be the targetobj. default=%(default)d')
  options = parser.parse_args()
  # Load the input video
  basename = os.path.splitext(os.path.basename(options.input))[0]
  print('Loading {0} ...'.format(options.input))
  cap = cv2.VideoCapture(options.input)
  fps = cap.get(cv2.CAP_PROP_FPS)
  fcount = int( cap.get(cv2.CAP_PROP_FRAME_COUNT) )
  width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH) )
  height = int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) )
  if not os.path.isfile(options.input) or fcount == 0:
    raise IOError('Failed to load input file: {}'.format(options.input))
  if options.info:
    print('  Number of frames: {}'.format(fcount))
    print('  FPS: {}'.format(fps))
    print('  Resolution: {0}x{1}'.format(width, height))
    print('  Duration: {0:.2f} seconds'.format(fcount/fps))
    exit()
  else:
    print('{0} has {1} frames'.format(options.input, fcount))
  # Prepare the output video
  if not options.visualize:
    vout_filename = basename + '_blended.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    vout = cv2.VideoWriter(vout_filename, fourcc, fps, (width, height))
  # Process the input video
  ret, blended = cap.read()
  beta = 1.0 - options.alpha
  morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (options.morph_open_ksize, options.morph_open_ksize))
  widgets = ['Processed: ', progressbar.Counter(), ' frames (', progressbar.Timer(), ')']
  pbar = progressbar.ProgressBar(widgets=widgets, maxval=int(fcount)).start()
  i = -1
  while True:
    i += 1
    ret, frame = cap.read()
    if i % int(1./options.sampling_factor) != 0:
      continue
    if frame is None:
      break
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    (thresh, bw) = cv2.threshold(gray, -1, 250, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    bw_smooth = cv2.medianBlur(bw, ksize=options.median_ksize)
    bw_open = cv2.morphologyEx(bw_smooth, cv2.MORPH_OPEN, morph_kernel)
    bw_cnt, contours, hierarchy = cv2.findContours(np.array(bw_open), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    found = False
    for cnt in contours:
      if options.min_targetobj_area < cv2.contourArea(cnt) < options.max_targetobj_area:
        if options.visualize:
          cv2.drawContours(frame, [cnt], -1, (255,0,0), thickness=2)
        found = True
        break
    # Visualize or generate the video
    if options.visualize:
      cv2.imshow('vidblend', blended)
      k = cv2.waitKey(int(1000./float(options.vis_fps)))
      if k == 27:     # ESC key
        break
    else:
      vout.write(blended)
    if found:
      mask = np.zeros_like(gray)
      cv2.drawContours(mask, [cnt], -1, color=255, thickness=cv2.FILLED)
      targetobj = np.array(frame)
      targetobj[mask==0] = 0
      blended[mask>0] = cv2.addWeighted(targetobj[mask>0], options.alpha, blended[mask>0], beta, 0)
    pbar.update(i)
  # Clean up
  pbar.finish()
  cap.release()
  if options.visualize:
    cv2.destroyAllWindows()
    print('Nothing has been generated. The script was run in visualization mode')
  else:
    vout.release()
    # Write output image and video
    png_filename = basename + '_blended.png'
    cv2.imwrite(png_filename, blended)
    print('Generated image: {}'.format(png_filename))
    print('Generated video: {}'.format(vout_filename))
