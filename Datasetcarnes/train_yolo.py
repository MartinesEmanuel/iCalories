import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Treina um modelo YOLO (Ultralytics) para o dataset local.')
    parser.add_argument('--data', default=str(base / 'data.yaml'), help='Caminho para o arquivo data.yaml')
    parser.add_argument('--model', default=str(base / 'yolov8n.pt'), help='Pesos iniciais (p.ex. yolov8n.pt)')
    parser.add_argument('--epochs', type=int, default=10, help='Número de épocas')
    parser.add_argument('--batch', type=int, default=16, help='Tamanho do batch')
    parser.add_argument('--imgsz', type=int, default=640, help='Tamanho das imagens (px)')
    parser.add_argument('--device', default='', help='Device: cpu ou id(s) da GPU (ex: 0 ou 0,1)')
    parser.add_argument('--project', default=str(base / 'runs' / 'train'), help='Pasta de saída do treino')
    parser.add_argument('--name', default='exp', help='Nome da execução (pasta dentro do project)')
    parser.add_argument('--exist_ok', action='store_true', help='Permite sobrescrever a pasta se já existir')
    return parser.parse_args()


def main():
    args = parse_args()
    print('Carregando modelo:', args.model)
    model = YOLO(args.model)

    print('Iniciando treino com as seguintes opções:')
    print(f' data={args.data} epochs={args.epochs} batch={args.batch} imgsz={args.imgsz}')

    model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=(args.device or None),
        project=args.project,
        name=args.name,
        exist_ok=args.exist_ok,
    )


if __name__ == '__main__':
    main()
