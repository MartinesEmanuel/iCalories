import os

caminho_dataset = r"C:\Users\caiot\Documents\Meus_Códigos\Visão Computacional\iCalories\Datasetcarnes\dataset"
classes = ["carne", "frango", "peixe"]

def renomear_sequencial(caminho_base, lista_classes):
    
    caminho_imagens = os.path.join(caminho_base, "images")
    caminho_labels = os.path.join(caminho_base, "labels")

    if not os.path.isdir(caminho_imagens) or not os.path.isdir(caminho_labels):
        print(f"Pastas 'images' e 'labels' não encontradas dentro de '{caminho_base}'")
        return

    contadores = {classe: 0 for classe in lista_classes}
    
    print("--- Iniciando processo de renomeação ---")

    lista_de_arquivos = sorted(os.listdir(caminho_imagens))

    for nome_arquivo_antigo in lista_de_arquivos:
        
        classe_identificada = None
        for classe in lista_classes:
            if nome_arquivo_antigo.startswith(f"{classe}_"):
                classe_identificada = classe
                break
        
        if not classe_identificada:
            print(f"Aviso: Pulando arquivo com nome não padronizado: '{nome_arquivo_antigo}'")
            continue

        contador_atual = contadores[classe_identificada]
        
        extensao = os.path.splitext(nome_arquivo_antigo)[1]
        
        novo_nome_arquivo = f"{classe_identificada}_{contador_atual:04d}{extensao}"

        caminho_antigo_img = os.path.join(caminho_imagens, nome_arquivo_antigo)
        caminho_novo_img = os.path.join(caminho_imagens, novo_nome_arquivo)

        nome_base_antigo = os.path.splitext(nome_arquivo_antigo)[0]
        caminho_antigo_label = os.path.join(caminho_labels, f"{nome_base_antigo}.txt")
        
        nome_base_novo = os.path.splitext(novo_nome_arquivo)[0]
        caminho_novo_label = os.path.join(caminho_labels, f"{nome_base_novo}.txt")

        print(f"Renomeando '{nome_arquivo_antigo}' -> '{novo_nome_arquivo}'")
        os.rename(caminho_antigo_img, caminho_novo_img)
        
        if os.path.exists(caminho_antigo_label):
            os.rename(caminho_antigo_label, caminho_novo_label)
        else:
            print(f"  Aviso: Label correspondente '{nome_base_antigo}.txt' não encontrado.")

        contadores[classe_identificada] += 1
        
    print("\n--- Processo Concluído! ---")
    for classe, total in contadores.items():
        print(f"Total de arquivos para a classe '{classe}': {total}")


if __name__ == "__main__":
    renomear_sequencial(caminho_dataset, classes)