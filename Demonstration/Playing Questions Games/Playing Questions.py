import random

respostas = {
    "Filmes": [],
    "Tecnologia": []
}
nome = input("Qual seu nome? ").strip()

listar_filmes = []
listar_tecnologia = []

def assunto():
    print(f"\nOlá {nome}! Sobre qual assunto você quer conversar?")
    print("1 - 🎬 Filmes")
    print("2 - 💻 Tecnologia")

    while True:
        opcao = input("\nDigite 1 ou 2: ").strip()
        if opcao == "1":
            print("Qual Filme você quer falar?")
            filme = input("Qual sua opiniao sobre o filme: ").strip()
            listar_filmes.append(filme)

            return f"Muito boa escolha! O filme {filme} é realmente interessante. O que mais você gosta sobre ele?"
        
        elif opcao == "2":
            print("Qual assunto de tecnologia você quer falar?")
            tecnologia = input("Qual sua opiniao sobre essa Tecnologia? ").strip()
            listar_tecnologia.append(tecnologia)

            return f"Interessante! A tecnologia {tecnologia} tem potencial. O que mais você gostaria de saber sobre ela?"
        else:
            print("Opção inválida. Digite 1 ou 2.")

def delchat():
    escolhido = assunto()
    print(f"\nÓtima escolha! Vamos conversar sobre {escolhido.capitalize()}!")

if __name__ == "__main__":
    delchat()
    print("\nObrigado por compartilhar suas opiniões! Foi ótimo conversar com você.")
    print(listar_filmes)
    print(listar_tecnologia)