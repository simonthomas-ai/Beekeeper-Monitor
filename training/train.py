#!/usr/bin/env python3
"""Train one experimental seven-class Vespa-focused YOLO baseline on licensed, verified images.
Fails closed if per-image provenance, splits, annotations or rights metadata are absent.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import yaml
from provenance import validate_provenance
try:
    from .class_schema import CLASS_NAMES
    from .evaluation import validate_per_class_summary
except ImportError:  # Supports direct execution: python training/train.py
    from class_schema import CLASS_NAMES
    from evaluation import validate_per_class_summary

CLASSES = list(CLASS_NAMES)
SPLITS=('train','val','test')
IMAGE_SUFFIXES={'.jpg','.jpeg','.png','.webp'}

def validate_image_file(path):
    """Decode each source image and reject mislabeled, animated or unsafe files."""
    import warnings
    from PIL import Image, UnidentifiedImageError

    expected_formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}
    expected_format = expected_formats.get(Path(path).suffix.lower())
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                actual_format = image.format
                width, height = image.size
                frame_count = getattr(image, "n_frames", 1)
                if width < 16 or height < 16:
                    raise ValueError(f'Image dimensions are too small: {path}')
                if width * height > 80_000_000:
                    raise ValueError(f'Image exceeds the 80 megapixel safety limit: {path}')
                if frame_count != 1:
                    raise ValueError(f'Animated images are not accepted as still training samples: {path}')
                image.verify()
            # verify() checks container integrity; load() also exercises pixel decoding.
            with Image.open(path) as image:
                image.load()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning,
            UnidentifiedImageError, OSError) as exc:
        raise ValueError(f'Image is corrupt, unreadable or unsafe: {path}') from exc

    if actual_format != expected_format:
        raise ValueError(
            f'Image extension/content mismatch for {path}: '
            f'expected {expected_format}, got {actual_format}'
        )
    return {'format': actual_format, 'width': width, 'height': height}


def validate(root):
    root=Path(root).resolve()
    config=yaml.safe_load((root/'training/data.yaml').read_text(encoding='utf-8'))
    base=(root/config['path']).resolve()
    if not base.is_relative_to(root):
        raise ValueError('Dataset path must remain inside repository')
    if [config['names'][i] for i in range(len(CLASSES))]!=CLASSES:
        raise ValueError('Class order mismatch')
    provenance_report = validate_provenance(base)
    report={'provenance': provenance_report}
    for split in SPLITS:
        image_dir=base/'images'/split
        label_dir=base/'labels'/split
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f'Missing actual images/labels for {split}')
        counts={name:0 for name in CLASSES}
        images=sorted(p for p in image_dir.rglob('*') if p.suffix.lower() in IMAGE_SUFFIXES)
        decoded_images = 0
        if not images:
            raise ValueError(f'No real images in {image_dir}')
        expected_labels = {
            image.relative_to(image_dir).with_suffix('.txt').as_posix()
            for image in images
        }
        actual_labels = {
            label.relative_to(label_dir).as_posix()
            for label in label_dir.rglob('*.txt')
        }
        if expected_labels != actual_labels:
            raise ValueError(f'Label files do not match images in {split}: missing={len(expected_labels-actual_labels)} orphan={len(actual_labels-expected_labels)}')
        for img in images:
            validate_image_file(img)
            decoded_images += 1
            relative=img.relative_to(image_dir).with_suffix('.txt')
            label=label_dir/relative
            if not label.is_file():
                raise ValueError(f'Missing annotation: {label}')
            for line in label.read_text(encoding='utf-8').splitlines():
                parts=line.split()
                if len(parts)!=5:
                    raise ValueError(f'Invalid YOLO annotation in {label}')
                try:
                    cls=int(parts[0])
                    coords=list(map(float,parts[1:]))
                except (ValueError, OverflowError) as exc:
                    raise ValueError(f'Invalid class/box in {label}') from exc
                if (
                    cls not in range(len(CLASSES))
                    or any(not 0 <= value <= 1 for value in coords)
                    or coords[2] <= 0 or coords[3] <= 0
                    or coords[0] - coords[2] / 2 < 0
                    or coords[1] - coords[3] / 2 < 0
                    or coords[0] + coords[2] / 2 > 1
                    or coords[1] + coords[3] / 2 > 1
                ):
                    raise ValueError(f'Invalid class/box in {label}')
                counts[CLASSES[cls]]+=1
        report[split]={'images':len(images),'decoded_images':decoded_images,'objects':counts}
    # Per-class coverage must be present in each split before claiming all models trained.
    for split in SPLITS:
        info = report[split]
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
    parser.add_argument('--accept-agpl',action='store_true', help='Explicitly accept AGPL-3.0 obligations for the current Ultralytics training path')
    parser.add_argument('--pretrained-model',default='yolo11n.pt')
    parser.add_argument('--pretrained-model-source-url',default='https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt')
    parser.add_argument('--pretrained-model-sha256',required=False)
    parser.add_argument('--confidence-threshold',type=float,default=0.5)
    parser.add_argument('--batch',type=int,default=16)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--patience',type=int,default=20)
    args=parser.parse_args()
    if not 1 <= args.epochs <= 500 or not 32 <= args.imgsz <= 4096:
        parser.error('--epochs must be 1..500 and --imgsz must be 32..4096')
    if not 1 <= args.batch <= 256:
        parser.error('--batch must be 1..256')
    if not 0 <= args.workers <= 32:
        parser.error('--workers must be 0..32')
    if not 0 <= args.seed <= 2147483647:
        parser.error('--seed must be 0..2147483647')
    if not 0 <= args.patience <= 200:
        parser.error('--patience must be 0..200')
    root=Path(__file__).resolve().parents[1]
    report=validate(root)
    print(json.dumps(report,indent=2))
    if args.validate_only:
        return
    if not args.accept_agpl:
        parser.error('The configured Ultralytics trainer has AGPL-3.0 obligations; pass --accept-agpl only after license review, or use a separately reviewed trainer.')
    pretrained_path=Path(args.pretrained_model).expanduser().resolve()
    if not pretrained_path.is_file():
        parser.error('--pretrained-model must be a locally verified checkpoint file; automatic network downloads are disabled')
    if not args.pretrained_model_sha256 or not re.fullmatch(r'[a-f0-9]{64}', args.pretrained_model_sha256):
        parser.error('--pretrained-model-sha256 must be the lowercase SHA-256 of the local checkpoint')
    pretrained_digest=hashlib.sha256(pretrained_path.read_bytes()).hexdigest()
    if pretrained_digest != args.pretrained_model_sha256:
        parser.error('Pretrained checkpoint SHA-256 mismatch')
    if not 0.0 <= args.confidence_threshold <= 1.0:
        parser.error('--confidence-threshold must be in 0..1; do not interpret this as a validated operating threshold')
    from urllib.parse import urlparse
    source_url=urlparse(args.pretrained_model_source_url)
    if source_url.scheme != 'https' or not source_url.netloc:
        parser.error('--pretrained-model-source-url must be an HTTPS provenance URL')
    import ultralytics
    if ultralytics.__version__ != '8.4.215':
        parser.error('This export path is tested against ultralytics==8.4.215; install the pinned training requirements first.')
    from ultralytics import YOLO
    # One Vespa-focused multi-class detector; it is not seven independent validated models.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp:
        cfg=yaml.safe_load((root/'training/data.yaml').read_text(encoding='utf-8'))
        cfg['path']=str((root/cfg['path']).resolve())
        resolved=Path(temp)/'data.yaml'
        resolved.write_text(yaml.safe_dump(cfg),encoding='utf-8')
        model=YOLO(str(pretrained_path))
        results=model.train(data=str(resolved),epochs=args.epochs,imgsz=args.imgsz,device=args.device,batch=args.batch,workers=args.workers,seed=args.seed,deterministic=True,patience=args.patience,project=str(root/'runs'),name='vespa-seven-class-detector',exist_ok=False)
        run_dir=Path(model.trainer.save_dir)
        best_weights=run_dir/'weights'/'best.pt'
        if not best_weights.is_file():
            raise FileNotFoundError('Training finished without a best.pt checkpoint; refusing to export a missing model')
        best=YOLO(str(best_weights))
        validation=best.val(data=str(resolved),split='test',plots=True)
        per_class_metrics = validate_per_class_summary(validation.summary(), CLASSES)
        exported=Path(best.export(format='onnx',imgsz=args.imgsz,nms=True,dynamic=False))
        digest=hashlib.sha256(exported.read_bytes()).hexdigest()
        model_dir=run_dir/'deployment'
        model_dir.mkdir(parents=True,exist_ok=False)
        model_target=model_dir/'detector.onnx'
        exported.replace(model_target)
        model_classes=[]
        for class_id,name in enumerate(CLASSES):
            model_classes.append({
                'id': class_id, 'label': name, 'threshold': args.confidence_threshold,
                'prey_detected': False,
            })
        manifest={
            'manifest_version': 1,
            'model_file': 'detector.onnx',
            'model_sha256': digest,
            'model_version': f'{pretrained_path.name};base-{pretrained_digest[:12]};ultralytics-{ultralytics.__version__}',
            'model_source_url': args.pretrained_model_source_url,
            'model_license': 'NOASSERTION',
            'license_review_status': 'not-reviewed',
            'inference_status': 'experimental',
            'input': {
                'name': 'images', 'width': args.imgsz, 'height': args.imgsz,
                'color': 'RGB', 'layout': 'NCHW', 'scale': '0..1',
                'resize_mode': 'letterbox',
            },
            'outputs': {
                'detections': 'output0',
                'box_format': 'xyxy_pixels_nms_matrix6',
            },
            'classes': model_classes,
        }
        manifest_path=model_dir/'model-manifest.json'
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        metrics_dict=getattr(validation,'results_dict',{}) or {}
        training_config={
            'epochs': args.epochs,
            'imgsz': args.imgsz,
            'device': args.device,
            'batch': args.batch,
            'workers': args.workers,
            'seed': args.seed,
            'deterministic': True,
            'patience': args.patience,
        }
        evidence={
            'status':'internal_test_split_only_not_independent_field_validation',
            'training_config': training_config,
            'dataset_validation':report,
            'test_metrics':{str(key):float(value) for key,value in metrics_dict.items()},
            'test_metrics_by_class':per_class_metrics,
            'test_metrics_scope':'untouched_internal_test_split_only; no field validation or confidence intervals',
            'onnx_sha256':digest,
            'pretrained_checkpoint_sha256':pretrained_digest,
            'pretrained_checkpoint_source_url':args.pretrained_model_source_url,
            'model_license':'NOASSERTION',
            'model_license_review':'not-reviewed; AGPL trainer acknowledgement does not approve checkpoint, dataset or output model rights',
            'confidence_thresholds':'experimental_not_calibrated',
        }
        (model_dir/'training-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print('Training and ONNX export completed. Model remains EXPERIMENTAL and all detections remain unverified.')
    print(f'Model artifact: {model_target}')
    print(f'Manifest: {manifest_path}')
    print('Do not enable field deployment until independent per-class evaluation and thresholds have been reviewed.')

if __name__=='__main__':
    main()
