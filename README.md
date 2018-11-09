# Installation
```bash
mkvirtualenv --python=/usr/bin/python2.7 vidblend
workon vidblend
pip install ipython numpy progressbar
```

# Usage

```
$ python vidblend.py -h
usage: vidblend.py [-h] [--info] [--visualize] [--vis-fps] [--alpha]
                   [--sampling-factor] [--median-ksize] [--morph-open-ksize]
                   [--min-targetobj-area] [--max-targetobj-area]
                   input

Video blender for moving objects on a static background

positional arguments:
  input                 Path to the input video

optional arguments:
  -h, --help            show this help message and exit
  --info                If set, ONLY shows the input video information

visualization:
  --visualize           If set, visualize ONLY the process. ESC to quit
  --vis-fps             The FPS for the visualization. default=30

blending:
  --alpha               Blending transparency. default=0.10
  --sampling-factor     Percentage of frames to be used. default=0.25

filtering:
  --median-ksize        Kernel size for the median noise filter. default=3
  --morph-open-ksize    Kernel size for open morphologic operation. default=11
  --min-targetobj-area
                        Min area to consider a countour to be the targetobj.
                        default=5000
  --max-targetobj-area
                        Max area to consider a countour to be the targetobj.
                        default=105000
```

# Examples

### Info

```bash
python vidblend.py Blending0_6-2.mp4 --info
python vidblend.py RT_6t2.mp4 --info
python vidblend.py RT_6t2e.mp4 --info
python vidblend.py SM_5t1.mp4 --info
python vidblend.py SM_6t2.mp4 --info
```

### Generation

```bash
python vidblend.py Blending0_6-2.mp4 --sampling-factor=0.15
python vidblend.py RT_6t2.mp4 --sampling-factor=1
python vidblend.py RT_6t2e.mp4 --sampling-factor=1
python vidblend.py SM_5t1.mp4 --sampling-factor=0.15
python vidblend.py SM_6t2.mp4 --sampling-factor=0.15
```

### Visualization

```bash
python vidblend.py Blending0_6-2.mp4 --visualize --vis-fps 10
python vidblend.py RT_6t2.mp4 --visualize --vis-fps 10
python vidblend.py RT_6t2e.mp4 --visualize --vis-fps 10
python vidblend.py SM_5t1.mp4 --visualize --vis-fps 10
python vidblend.py SM_6t2.mp4 --visualize --vis-fps 10
python vidblend.py RT_6t2.mp4 --visualize --vis-fps 10
```
