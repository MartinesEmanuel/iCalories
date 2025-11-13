"""
Script de treino avançado (OTM = "Optimização e Transfer e Melhoria").

Este arquivo demonstra técnicas úteis para treinar/ajustar um modelo YOLOv8:
- congelamento de camadas (freeze)
- treino progressivo em duas fases (freeze -> unfreeze)
- data augmentation (augment)
- ajuste de learning rate (lr0)
- uso de cache de imagens (cache)
- opção para retomar treino (resume)

Use com atenção e ajuste parâmetros conforme seu dataset.

Exemplo (PowerShell):
python .\train_yolo_otm.py --epochs 60 --batch 8 --freeze 10 --progressive --freeze_epochs 20 --augment --lr0 0.001 --cache ram
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Treino avançado YOLOv8 com técnicas de fine-tuning e otimização')

    # Caminhos e configuração básica
    parser.add_argument('--data', default=str(base / 'data.yaml'), help='Caminho para data.yaml')
    parser.add_argument('--model', default=str(base / 'yolov8n.pt'), help='Pesos iniciais (p.ex. yolov8n.pt)')
    parser.add_argument('--project', default=str(base / 'runs' / 'train_otm'), help='Pasta de saída do treino')
    parser.add_argument('--name', default='exp_otm', help='Nome da execução (pasta dentro do project)')
    parser.add_argument('--exist_ok', action='store_true', help='Permite sobrescrever a pasta se já existir')

    # Treino e hardware
    parser.add_argument('--epochs', type=int, default=50, help='Total de épocas (se progressive, soma das fases)')
    parser.add_argument('--batch', type=int, default=16, help='Tamanho do batch')
    parser.add_argument('--imgsz', type=int, default=640, help='Tamanho das imagens (px)')
    parser.add_argument('--device', default='', help='Device: cpu ou id(s) da GPU (ex: 0 ou 0,1)')

    # Fine-tuning / transferência
    parser.add_argument('--freeze', type=int, default=10, help='Número de camadas a congelar (primeira fase)')
    parser.add_argument('--progressive', action='store_true', help='Fazer treino em duas fases: freeze -> unfreeze')
    parser.add_argument('--freeze_epochs', type=int, default=20, help='Épocas da fase congelada (apenas se --progressive)')
    parser.add_argument('--resume', action='store_true', help='Retomar treino (resume=True)')

    # Técnicas de otimização
    parser.add_argument('--augment', action='store_true', help='Ativa data augmentation (aleatório)')
    parser.add_argument('--lr0', type=float, default=0.01, help='Learning rate inicial (lr0)')
    parser.add_argument('--cache', choices=['', 'ram', 'disk'], default='', help='Cache de imagens: "ram", "disk" ou vazio')

    return parser.parse_args()


def train_stage(model, stage_name: str, epochs: int, freeze: int, args):
    """Executa um estágio de treino com parâmetros explícitos e imprime informações."""
    if epochs <= 0:
        print(f"[SKIP] {stage_name}: epochs={epochs} <= 0")
        return

    print(f"\n[START] {stage_name}: epochs={epochs}, freeze={freeze}, augment={args.augment}, lr0={args.lr0}, cache={args.cache}")

    # cache para passagem para ultralytics: False/''/ram/disk
    cache_param = args.cache if args.cache else False

    model.train(
        data=args.data,
        epochs=epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=(args.device or None),
        project=args.project,
        name=args.name,
        exist_ok=args.exist_ok,
        freeze=freeze,
        augment=args.augment,
        lr0=args.lr0,
        cache=cache_param,
        resume=args.resume,
    )


def main():
    args = parse_args()

    print('Carregando modelo base:', args.model)
    model = YOLO(args.model)

    # Estratégia: treino progressivo em duas fases (congelado -> descongelado)
    if args.progressive:
        # A primeira fase é com freeze (congelar backbone), por 'freeze_epochs'
        stage1_epochs = min(args.freeze_epochs, args.epochs)
        stage2_epochs = max(args.epochs - stage1_epochs, 0)

        # Fase 1: congelar camadas iniciais (estabilizar cabeças)
        train_stage(model, 'Fase 1 (congelado)', stage1_epochs, args.freeze, args)

        # Fase 2: descongelar (treino fino de todo o modelo)
        # Recomenda-se reduzir o lr para a fase final — aqui aplicamos lr0/10 por convenção
        if stage2_epochs > 0:
            # ajusta lr para fase 2 (mais suave)
            old_lr = args.lr0
            args.lr0 = max(args.lr0 / 10.0, 1e-6)
            print(f"\n[INFO] Ajustando lr para fase 2: {old_lr} -> {args.lr0}")

            # Antes de iniciar a fase 2, recarregamos os pesos do último run (best.pt ou last.pt)
            # isso evita problemas internos do objeto YOLO que podem ocorrer quando se reutiliza
            # a mesma instância após uma chamada completa de train().
            weights_dir = Path(args.project) / args.name / 'weights'
            best_pt = weights_dir / 'best.pt'
            last_pt = weights_dir / 'last.pt'
            if best_pt.exists():
                weights_to_load = best_pt
            elif last_pt.exists():
                weights_to_load = last_pt
            else:
                weights_to_load = Path(args.model)

            print(f"[INFO] Carregando pesos para fase 2: {weights_to_load}")
            model = YOLO(str(weights_to_load))

            # Ao recarregar os pesos, desativamos resume para evitar conflitos internos
            # (se você quiser usar resume, passe --resume na chamada inicial em vez
            # de depender de resume entre fases).
            args.resume = False

            train_stage(model, 'Fase 2 (descongelado)', stage2_epochs, 0, args)
    else:
        # Treino único com os parâmetros escolhidos (freeze pode ser 0 para treinar tudo)
        train_stage(model, 'Treino único', args.epochs, args.freeze, args)


if __name__ == '__main__':
    main()
