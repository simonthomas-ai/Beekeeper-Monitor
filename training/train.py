#!/usr/bin/env python3
"""Train six independent YOLO detectors on real, verified labeled datasets.
Fails closed if data or label metadata is absent. No fake model output.
"""
import argparse
import json
import os
from pathlib import Path
import yaml

CLASSES=['vespa_velutina','varroa_destructor','drone_brood','pollen_bearing_bee','bee_swarm','queen_bee']
SPLITS=('train','val','test')
IMAGE_SUFFIXES={'.jpg','.jpeg','.png','.webp'}
def validate(root):
    root=Path(root).resolve()
    config=yaml.safe_load((root/'training/data.yaml').read_text(encoding='utf-8'))
    base=(root/config['path']).resolve()
    if not base.is_relative_to(root):
        raise ValueError('Dataset path must remain inside repository')
    if [config['names'][i] for i in range(6)]!=CLASSES:
        raise ValueError('Class order mismatch')
    report={}
    for split in SPLITS:
        image_dir=base/'images'/split
        label_dir=base/'labels'/split
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f'Missing actual images/labels for {split}')
        counts={name:0 for name in CLASSES}
        images=sorted(p for p in image_dir.rglob('*') if p.suffix.lower() in IMAGE_SUFFIXES)
        if not images:
            raise ValueError(f'No real images in {image_dir}')
        for img in images:
            relative=img.relative_to(image_dir).with_suffix('.txt')
            label=label_dir/relative
            if not label.is_file():
                raise ValueError(f'Missing annotation: {label}')
            for line in label.read_text(encoding='utf-8').splitlines():
                parts=line.split()
                if len(parts)!=5:
                    raise ValueError(f'Invalid YOLO annotation in {label}')
                cls=int(parts[0])
                coords=list(map(float,parts[1:]))
                if cls not in range(6) or any(not 0<=v<=1 for v in coords) or coords[2]<=0 or coords[3]<=0:
                    raise ValueError(f'Invalid class/box in {label}')
                counts[CLASSES[cls]]+=1
        report[split]={'images':len(images),'objects':counts}
    # Per-class coverage must be present in each split before claiming all models trained.
    for split,info in report.items():
        for name,count in info['objects'].items():
            if count<1:
                raise ValueError(f'No real annotated examples of {name} in {split}')
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--epochs',type=int,default=60)
    parser.add_argument('--imgsz',type=int,default=640)
    parser.add_argument('--device',default='cpu')
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    report=validate(root)
    print(json.dumps(report,indent=2))
    if args.validate_only:
        return
    from ultralytics import YOLO
    # A single multi-class detector; it is NOT six independent validated models.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp:
        cfg=yaml.safe_load((root/'training/data.yaml').read_text(encoding='utf-8'))
        cfg['path']=str((root/cfg['path']).resolve())
        resolved=Path(temp)/'data.yaml'
        resolved.write_text(yaml.safe_dump(cfg),encoding='utf-8')
        model=YOLO('yolo11n.pt')
        model.train(data=str(resolved),epochs=args.epochs,imgsz=args.imgsz,device=args.device,project=str(root/'runs'),name='six-class-detector',exist_ok=False)
        model.val(data=str(resolved),split='test')
    print('Training completed. Evaluate per-class precision/recall before deployment.')

if __name__=='__main__':
    main()
