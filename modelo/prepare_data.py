import os
import shutil
import random

caminho_dados_crus = r"C:\Users\caiot\Documents\Meus_Códigos\Visão Computacional\iCalories\modelo\dados_crus"
caminho_dataset_final = r"C:\Users\caiot\Documents\Meus_Códigos\Visão Computacional\iCalories\modelo\dataset_final"

classes = ["carne", "frango", "peixe"]

split_ratio = {
    "train": 0.7,  # 70% para treino
    "valid": 0.2,  # 20% para validação
    "test": 0.1    # 10% para teste
}

def criar_pastas_destino(caminho_base, splits):

    for split in splits:

        for subpasta in ["images", "labels"]:

            caminho = os.path.join(caminho_base, split, subpasta)
            os.makedirs(caminho, exist_ok=True)

    print("Estrutura de pastas de destino criada.")

def preparar_dataset_completo(origem, destino, lista_classes, ratio):

    criar_pastas_destino(destino, ratio.keys())
    contador_geral = {classe: 0 for classe in lista_classes}
    print("\n--- Iniciando preparação completa do dataset ---")

    for classe in lista_classes:

        print(f"\nProcessando classe: '{classe}'...")
        arquivos_da_classe = []

        for root, _, files in os.walk(origem):

            for file in files:

                if file.lower().startswith(f"{classe}_") and file.lower().endswith(('.png', '.jpg', '.jpeg')):

                    caminho_completo = os.path.join(root, file)
                    arquivos_da_classe.append(caminho_completo)
        
        if not arquivos_da_classe:

            print(f"Nenhum arquivo encontrado para a classe '{classe}'.")
            continue
            
        random.shuffle(arquivos_da_classe)

        total_arquivos = len(arquivos_da_classe)
        ponto_corte_train = int(total_arquivos * ratio["train"])
        ponto_corte_valid = ponto_corte_train + int(total_arquivos * ratio["valid"])
        
        arquivos_train = arquivos_da_classe[:ponto_corte_train]
        arquivos_valid = arquivos_da_classe[ponto_corte_train:ponto_corte_valid]
        arquivos_test = arquivos_da_classe[ponto_corte_valid:]
        
        splits = {
            "train": arquivos_train,
            "valid": arquivos_valid,
            "test": arquivos_test
        }

        print(f"Encontrados {total_arquivos} arquivos. Dividindo em: "
              f"{len(arquivos_train)} treino, {len(arquivos_valid)} validação, {len(arquivos_test)} teste.")

        for nome_split, lista_arquivos in splits.items():

            for caminho_original_img in lista_arquivos:

                contador_atual = contador_geral[classe]
                extensao = os.path.splitext(caminho_original_img)[1]
                novo_nome_img = f"{classe}_{contador_atual:04d}{extensao}"
                caminho_destino_img = os.path.join(destino, nome_split, "images", novo_nome_img)
                shutil.copy2(caminho_original_img, caminho_destino_img)


                caminho_original_label_tentativa1 = f"{os.path.splitext(caminho_original_img)[0]}.txt"
                caminho_original_label_tentativa2 = caminho_original_img.replace("images", "labels").replace(extensao, ".txt")
                caminho_original_label = ""

                if os.path.exists(caminho_original_label_tentativa1):
                    caminho_original_label = caminho_original_label_tentativa1

                elif os.path.exists(caminho_original_label_tentativa2):
                    caminho_original_label = caminho_original_label_tentativa2

                if caminho_original_label:

                    novo_nome_label = f"{classe}_{contador_atual:04d}.txt"
                    caminho_destino_label = os.path.join(destino, nome_split, "labels", novo_nome_label)
                    shutil.copy2(caminho_original_label, caminho_destino_label)

                else:
                    print(f"  Aviso: Label correspondente para '{os.path.basename(caminho_original_img)}' não encontrado.")

                contador_geral[classe] += 1

    print("\n--- Processo Concluído! ---")
    print(f"Contagem final de arquivos por classe: {contador_geral}")

if __name__ == "__main__":

    if os.path.exists(caminho_dataset_final):
        shutil.rmtree(caminho_dataset_final)
        print(f"Pasta '{caminho_dataset_final}' antiga removida.")
        
    preparar_dataset_completo(caminho_dados_crus, caminho_dataset_final, classes, split_ratio)