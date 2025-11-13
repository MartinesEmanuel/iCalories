import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Roda inferência com um modelo YOLO (Ultralytics).')
    parser.add_argument('--weights', default=str(base / 'yolov8n.pt'), help='Caminho para pesos (p.ex. runs/train/exp/weights/best.pt)')
    parser.add_argument('--source', default=str(base / 'test' / 'images'), help='Fonte: arquivo, pasta, vídeo ou webcam (use 0)')
    parser.add_argument('--imgsz', type=int, default=640, help='Tamanho das imagens')
    parser.add_argument('--conf', type=float, default=0.25, help='Confiança mínima')
    parser.add_argument('--iou', type=float, default=0.45, help='IOU para NMS')
    parser.add_argument('--device', default='', help='Device: cpu ou id(s) da GPU (ex: 0 ou 0,1)')
    parser.add_argument('--project', default=str(base / 'runs' / 'detect'), help='Pasta de saída')
    parser.add_argument('--name', default='predict', help='Nome da execução (pasta dentro do project)')
    parser.add_argument('--save_txt', action='store_true', help='Salvar boxes em TXT (formato YOLO)')
    return parser.parse_args()


def main():
    args = parse_args()
    print('Carregando pesos:', args.weights)
    model = YOLO(args.weights)

    print('Executando predição: source=', args.source)
    model.predict(
        source=args.source,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        device=(args.device or None),
        save=True,
        save_txt=args.save_txt,
        project=args.project,
        name=args.name,
    )


if __name__ == '__main__':
    main()
