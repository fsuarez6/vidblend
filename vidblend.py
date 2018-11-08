#! /usr/bin/env python
"""
# Installation
mkvirtualenv --python=/usr/bin/python2.7 vidblend
workon vidblend
pip install ipython numpy progressbar

# Execution
Place the script in the same folder with the video and specify
the filename
$ python vidblend.py
"""

import cv2
import numpy as np
import progressbar

## Parameters
alpha = 0.1
visualize = True
filename = 'Blending0_6-2.mp4'
sampling_factor = 1./6.
##

print 'Loading {0} ...'.format(filename)
cap = cv2.VideoCapture(filename)

fps = cap.get(cv2.CAP_PROP_FPS)
fcount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print '{0} has {1} frames'.format(filename, fcount)

ret, blended = cap.read()

beta = 1.0 - alpha
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
widgets = ['Processed: ', progressbar.Counter(), ' frames (', progressbar.Timer(), ')']
pbar = progressbar.ProgressBar(widgets=widgets, maxval=int(fcount)).start()
i = -1
while True:
  i += 1
  ret, frame = cap.read()
  if i % int(1./sampling_factor) != 0:
    continue
  if frame is None:
    break
  gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
  (thresh, bw) = cv2.threshold(gray, -1, 250, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  bw_smooth = cv2.medianBlur(bw, ksize=5)
  bw_open = cv2.morphologyEx(bw_smooth, cv2.MORPH_OPEN, kernel)
  bw_cnt, contours, hierarchy = cv2.findContours(np.array(bw_open), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  found = False
  for cnt in contours:
    if 5000 < cv2.contourArea(cnt) < 105000:
      if visualize:
        #~ cv2.drawContours(frame, [cnt], -1, (255,0,0), thickness=2)
		pass
      found = True
      break
  # Visualize
  if visualize:
    cv2.imshow('frame', blended)
    k = cv2.waitKey(1)
    if k == 27:
      break
  if found:
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [cnt], -1, color=255, thickness=cv2.FILLED)
    snake = np.array(frame)
    snake[mask==0] = 0
    blended[mask>0] = cv2.addWeighted(snake[mask>0], alpha, blended[mask>0], beta, 0)
  pbar.update(i)
pbar.finish()
cap.release()
if visualize:
  cv2.destroyAllWindows()

cv2.imwrite('blended.png', blended)
