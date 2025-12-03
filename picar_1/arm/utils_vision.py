# utils_vision.py
def pick_center_target(boxes, W=640, H=480):
    """가장 중앙에 가까우면서 conf 높은 박스 선택"""
    if not boxes:
        return None
    cx0, cy0 = W//2, H//2
    def score(b):
        x1,y1,x2,y2,cls,conf = b
        cx, cy = (x1+x2)//2, (y1+y2)//2
        return -((cx-cx0)**2 + (cy-cy0)**2) + 2000*conf
    return max(boxes, key=score)

def bbox_center(b):
    x1,y1,x2,y2,cls,conf = b
    return ( (x1+x2)//2, (y1+y2)//2 )

def classify_lr(cx, W, band_ratio=(0.35, 0.65)):
    """왼/가운데/오른쪽 판정"""
    left_edge  = int(W * band_ratio[0])
    right_edge = int(W * band_ratio[1])
    if cx < left_edge:
        return "LEFT"
    elif cx > right_edge:
        return "RIGHT"
    else:
        return "CENTER"
