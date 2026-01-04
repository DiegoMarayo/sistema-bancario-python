import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


# ================= CLIENTES =================

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if conta not in self.contas:
            print("\n@@@ Conta não pertence a este cliente! @@@")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# ================= CONTAS =================

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido! @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente! @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido! @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

    def extrato(self):
        print("\n================ EXTRATO ================")
        if not self.historico.transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for t in self.historico.transacoes:
                print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")

        print(f"\nSaldo atual: R$ {self.saldo:.2f}")
        print("========================================")


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = len(
            [t for t in self.historico.transacoes if t["tipo"] == "Saque"]
        )

        if valor > self._limite:
            print("\n@@@ Valor excede o limite de saque! @@@")
            return False

        if saques_realizados >= self._limite_saques:
            print("\n@@@ Limite diário de saques atingido! @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
Agência:\t{self.agencia}
Conta:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""


# ================= HISTÓRICO =================

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return tuple(self._transacoes)

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })


# ================= TRANSAÇÕES =================

class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


# ================= FUNÇÕES AUXILIARES =================

def menu():
    texto = """\
=============== MENU ===============
[d] Depositar
[s] Sacar
[e] Extrato
[nc] Nova conta
[lc] Listar contas
[nu] Novo usuário
[q] Sair
=> """
    return input(textwrap.dedent(texto))


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def selecionar_conta(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("\nSelecione a conta:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"[{i}] Conta {conta.numero}")

    try:
        opcao = int(input("=> ")) - 1
        return cliente.contas[opcao]
    except (ValueError, IndexError):
        print("\n@@@ Opção inválida! @@@")
        return None


def ler_valor(msg):
    try:
        return float(input(msg))
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        return None


# ================= OPERAÇÕES =================

def depositar(clientes):
    cpf = input("CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = ler_valor("Valor do depósito: ")
    if valor is None:
        return

    conta = selecionar_conta(cliente)
    if conta:
        cliente.realizar_transacao(conta, Deposito(valor))


def sacar(clientes):
    cpf = input("CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = ler_valor("Valor do saque: ")
    if valor is None:
        return

    conta = selecionar_conta(cliente)
    if conta:
        cliente.realizar_transacao(conta, Saque(valor))


def criar_cliente(clientes):
    cpf = input("CPF (11 dígitos): ")

    if not cpf.isdigit() or len(cpf) != 11:
        print("\n@@@ CPF inválido! @@@")
        return

    if filtrar_cliente(cpf, clientes):
        print("\n@@@ CPF já cadastrado! @@@")
        return

    nome = input("Nome completo: ")
    nascimento = input("Data nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço completo: ")

    clientes.append(PessoaFisica(nome, nascimento, cpf, endereco))
    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero, clientes, contas):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente, numero)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 40)
        print(conta)


# ================= MAIN =================

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            cpf = input("CPF: ")
            cliente = filtrar_cliente(cpf, clientes)
            if cliente:
                conta = selecionar_conta(cliente)
                if conta:
                    conta.extrato()
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(len(contas) + 1, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("\n@@@ Opção inválida! @@@")


main()
