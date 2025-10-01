from ultralytics import YOLO

model = YOLO('yolov8n.pt')
data_config_path = r'C:\Users\caiot\Documents\Meus_Códigos\Visão Computacional\iCalories\modelo\data.yaml'

def treinar_modelo():
    
    print("Iniciando o treinamento do modelo...")
    
    results = model.train(
        data=data_config_path,    
        epochs=100,               
        imgsz=640,                
        batch=4,                 
        name='yolov8n_run1'  
    )
    
    print("--- Treinamento Concluído! ---")
    print("Seu modelo treinado foi salvo na pasta 'runs/detect/'.")
    print("O melhor modelo é o 'best.pt' dentro da subpasta 'weights'.")

if __name__ == '__main__':
    treinar_modelo()