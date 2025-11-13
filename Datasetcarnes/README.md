# Scripts para treinar e rodar YOLO (Ultralytics)

Exemplos de uso no Windows PowerShell (rodar a partir da raiz do repositório):

Treinar:

```powershell
python .\Datasetcarnes\train_yolo.py --epochs 50 --batch 8 --model Datasetcarnes\yolov8n.pt --data Datasetcarnes\data.yaml
```

Fazer inferência (usar pesos resultantes do treino ou `yolov8n.pt`):

```powershell
python .\Datasetcarnes\run_yolo.py --weights Datasetcarnes\runs\train\exp\weights\best.pt --source Datasetcarnes\test\images --save_txt
```

Notas:
- Os scripts usam a biblioteca `ultralytics` (instale com `pip install -r Datasetcarnes/requirements.txt`).
- Ajuste `--device` para `cpu` ou `0` (GPU) conforme necessário.
- `data.yaml` deve apontar para as pastas `train`, `val` e `names` apropriadas (o arquivo está em `Datasetcarnes/data.yaml`).
