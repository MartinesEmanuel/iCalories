"""Gera plots de análise (results.png, confusion_matrix.png) a partir de um checkpoint YOLO (last.pt/best.pt).

Uso:
    python generate_plots.py --run runs/train/exp_name
    python generate_plots.py --checkpoint runs/train/exp_name/weights/last.pt --imgsz 640 --batch 16

Funcionalidades:
- localiza checkpoint (prioridade: --checkpoint > last.pt > best.pt)
- executa `YOLO(checkpoint).val(..., plots=True, save_json=True)`
- localiza a pasta de validação criada pelo Ultralytics (p.ex. runs/val*, runs/detect/val*)
- copia `results.png` e `confusion_matrix.png` para a pasta do run (se informado)
- se não houver `results.png`, gera um gráfico simples a partir de `results.csv` (fallback) usando matplotlib
"""

import argparse
import time
import csv
import shutil
import subprocess
from pathlib import Path
from ultralytics import YOLO


def find_latest_val_dir(runs_base: Path) -> Path | None:
    candidates = []
    # comuns: runs/val*, runs/detect/val*
    v = runs_base / 'val'
    if v.exists():
        candidates.extend([d for d in v.iterdir() if d.is_dir()])
    detect = runs_base / 'detect'
    if detect.exists():
        candidates.extend([d for d in detect.iterdir() if d.is_dir() and d.name.startswith('val')])
    # fallback recursivo
    if not candidates:
        for d in runs_base.rglob('val*'):
            if d.is_dir():
                candidates.append(d)
    if not candidates:
        return None
    return max(candidates, key=lambda d: d.stat().st_mtime)


def find_result_pngs(val_dir: Path):
    patterns = ['results*.png', 'result*.png', '*results.png', 'confusion*.png', '*confusion*.png', '*.png']
    candidates = []
    for pat in patterns:
        candidates.extend(val_dir.rglob(pat))
    # filtrar arquivos muito pequenos (prováveis incompletos)
    candidates = [p for p in set(candidates) if p.is_file() and p.stat().st_size > 1000]
    results = sorted([p for p in candidates if 'result' in p.name.lower()], key=lambda p: p.stat().st_mtime, reverse=True)
    confusion = sorted([p for p in candidates if 'confusion' in p.name.lower()], key=lambda p: p.stat().st_mtime, reverse=True)
    others = sorted([p for p in candidates if p not in results + confusion], key=lambda p: p.stat().st_mtime, reverse=True)
    return results + confusion + others


def create_results_png_from_csv(src_csv: Path, dest_png: Path) -> bool:
    if not src_csv.exists():
        return False
    epochs = []
    map50 = []
    map5095 = []
    # tentar ler CSV com cabeçalhos variados
    try:
        with src_csv.open('r', encoding='utf-8') as f:
            # detectar delimitador automático? assumimos vírgula
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                # campos possíveis
                e = row.get('epoch') or row.get('#') or str(i)
                try:
                    epochs.append(int(float(e)))
                except Exception:
                    epochs.append(i)
                m50 = row.get('metrics/mAP50(B)') or row.get('metrics/mAP50') or row.get('mAP50') or row.get('map50')
                m5095 = row.get('metrics/mAP50-95(B)') or row.get('metrics/mAP50-95') or row.get('mAP50-95') or row.get('map50_95')
                try:
                    map50.append(float(m50) if m50 not in (None, '') else float('nan'))
                except Exception:
                    map50.append(float('nan'))
                try:
                    map5095.append(float(m5095) if m5095 not in (None, '') else float('nan'))
                except Exception:
                    map5095.append(float('nan'))
    except Exception as e:
        print('Erro lendo CSV:', e)
        return False

    if not epochs:
        return False

    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib não instalado — instale com: pip install matplotlib')
        return False

    plt.figure(figsize=(8, 4))
    plt.plot(epochs, map50, label='mAP50', marker='o')
    plt.plot(epochs, map5095, label='mAP50-95', marker='x')
    plt.xlabel('Epoch')
    plt.ylabel('mAP')
    plt.title(src_csv.parent.name)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    try:
        plt.savefig(str(dest_png), dpi=150)
        plt.close()
        print('Gerado fallback results.png em', dest_png)
        return True
    except Exception as e:
        print('Erro ao salvar fallback PNG:', e)
        return False


def parse_args():
    parser = argparse.ArgumentParser(description='Gera plots (results.png, confusion_matrix) a partir de checkpoint YOLO')
    parser.add_argument('--run', type=str, help='Pasta do run (ex: runs/train/exp_name)')
    parser.add_argument('--checkpoint', type=str, help='Checkpoint direto (ex: runs/train/exp/weights/last.pt)')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--open', action='store_true', help='Abrir results.png quando pronto')
    return parser.parse_args()


def main():
    args = parse_args()
    base = Path(__file__).resolve().parent

    # determinar checkpoint
    ckpt = None
    if args.checkpoint:
        ckpt = Path(args.checkpoint)
    elif args.run:
        run_weights = Path(args.run) / 'weights'
        last = run_weights / 'last.pt'
        best = run_weights / 'best.pt'
        if last.exists():
            ckpt = last
        elif best.exists():
            ckpt = best
        else:
            raise SystemExit(f'Nenhum checkpoint encontrado em {run_weights}')
    else:
        raise SystemExit('Forneça --run ou --checkpoint')

    print('Usando checkpoint:', str(ckpt))

    # executar validação (gera plots)
    model = YOLO(str(ckpt))
    print('Rodando validação, aguarde...')
    res = model.val(data=str(base / 'data.yaml'), imgsz=args.imgsz, batch=args.batch, plots=True, save_json=True)
    time.sleep(1)

    runs_base = base / 'runs'
    val_dir = find_latest_val_dir(runs_base)
    if val_dir is None:
        print('Pasta runs/val/detect/val* não encontrada — verifique onde o ultralytics salvou os plots')
        return

    print('Val directory encontrado (mais recente):', val_dir)

    # procurar PNGs gerados
    pngs = []
    for _ in range(10):
        pngs = find_result_pngs(val_dir)
        if pngs:
            break
        time.sleep(0.5)

    if not pngs:
        print('Nenhum PNG de resultado encontrado em', val_dir)
    else:
        print('Arquivos PNG encontrados:')
        for p in pngs:
            print('  -', p.name, '-', p.stat().st_size, 'bytes')

    # copiar para run se solicitado
    if args.run:
        dest = Path(args.run)
        dest.mkdir(parents=True, exist_ok=True)
        copied = []
        for p in pngs:
            target = dest / p.name
            try:
                shutil.copy2(p, target)
                copied.append(target)
                print(f'Copiado {p} -> {target}')
            except Exception as e:
                print('Falha ao copiar', p, '->', target, e)

        # se não houver results.png copiado, tentar gerar a partir de results.csv
        results_png_dest = dest / 'results.png'
        if not results_png_dest.exists():
            run_csv = dest / 'results.csv'
            val_csv = val_dir / 'results.csv'
            csv_to_use = run_csv if run_csv.exists() else (val_csv if val_csv.exists() else None)
            if csv_to_use:
                created = create_results_png_from_csv(csv_to_use, results_png_dest)
                if created and args.open:
                    subprocess.run(['start', str(results_png_dest)], shell=True)
            else:
                print('Nenhum results.csv encontrado em', dest, 'ou', val_dir, '=> não foi possível gerar results.png automaticamente.')
        else:
            if args.open:
                subprocess.run(['start', str(results_png_dest)], shell=True)
    else:
        # se não informou run, abrir o primeiro png encontrado
        if args.open and pngs:
            subprocess.run(['start', str(pngs[0])], shell=True)

    # imprimir resumo das métricas retornadas pelo val
    try:
        print('results_dict:', res[0].results_dict if isinstance(res, list) else getattr(res, 'results_dict', res))
    except Exception:
        pass


if __name__ == '__main__':
    main()

