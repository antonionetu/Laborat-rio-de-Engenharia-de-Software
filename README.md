# Para Rodar o Projeto

## Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/) instalado no sistema
---

## 🧩 Passos para execução

1. **Crie o ambiente virtual**
   ```bash
   python -m venv venv
   ```

2. **Ative o ambiente virtual**
   - **Windows**
     ```bash
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**
     ```bash
     source venv/bin/activate
     ```

3. **(Opcional) Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplique as migrações do banco de dados**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário (admin)**
   ```bash
   python manage.py createsuperuser
   ```
   > Siga as instruções para definir nome de usuário, e-mail e senha.

6. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

7. **Acesse a aplicação no navegador**
   ```
   http://127.0.0.1:8000/
   ```

---

## 💡 Dica
Se o projeto usa variáveis de ambiente, crie um arquivo `.env` na raiz do projeto e defina as chaves necessárias antes de iniciar o servidor.

---

© 2025 — Projeto Django
