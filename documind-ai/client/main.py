import typer
from pathlib import Path
from rich import print
from api_client import CorpusClient
from auth import login as api_login
from sample_data import documents


app = typer.Typer(
    name="documind",
    help="DocuMind AI - Intelligent Corpus Assistant"
)


client = CorpusClient()


@app.command()
def search(query: str):

    print("[bold green]Searching Documents...[/bold green]\n")

    results = client.search(query)

    if not results:
        print("No documents found")
        return

    for doc in results:
        print(f"""
[bold cyan]ID:[/bold cyan] {doc['id']}
[bold cyan]Category:[/bold cyan] {doc['category']}
[bold cyan]Title:[/bold cyan] {doc['title']}
""")


@app.command()
def view(id: int):

    doc = client.get_document(id)

    if doc:
        print(f"""
[bold cyan]Document Details[/bold cyan]

ID:
{doc['id']}

Category:
{doc['category']}

Title:
{doc['title']}

Content:
{doc['content']}
""")

    else:
        print("Document not found")


@app.command()
def summarize(id: int):

    doc = client.get_document(id)

    if doc:

        print("[bold green]Generating AI Summary...[/bold green]\n")

        summary = doc["content"][:100] + "..."

        print(f"""
[bold cyan]Summary:[/bold cyan]

{summary}
""")

    else:
        print("Document not found")


@app.command()
def categories():

    print("[bold green]Available Categories:[/bold green]\n")

    category_list = set()

    for doc in documents:
        category_list.add(doc["category"])

    for category in sorted(category_list):
        print(f"• {category}")


@app.command()
def category(name: str):

    print(
        f"[bold green]Documents in {name}:[/bold green]\n"
    )

    found = False

    for doc in documents:

        if doc["category"].lower() == name.lower():

            found = True

            print(f"""
[bold cyan]ID:[/bold cyan] {doc['id']}
[bold cyan]Title:[/bold cyan] {doc['title']}
[bold cyan]Content:[/bold cyan] {doc['content']}
""")


    if not found:
        print("No documents found in this category")


@app.command()
def upload(file: str):

    path = Path(file)

    if not path.exists():
        print("[bold red]Error:[/bold red] File not found.")
        return

    print("[bold green]Uploading document...[/bold green]\n")

    print(f"File Name : {path.name}")
    print(f"File Size : {path.stat().st_size} bytes")

    print("\n[bold green]Upload Successful![/bold green]")
    print("Document added to DocuMind AI (Demo Mode)")


@app.command()
def login():
    phone = typer.prompt("Phone")
    password = typer.prompt("Password", hide_input=True)

    print("\n[bold green]Logging in...[/bold green]\n")

    response = api_login(phone, password)

    if response.status_code == 200:
        print("[bold green]Login Successful![/bold green]")
        print(response.json())
    elif response.status_code == 401:
        print("[bold red]Login failed: Incorrect phone number or password.[/bold red]")
    else:
        print(f"[bold red]Error {response.status_code}[/bold red]")
        print(response.text)


@app.command()
def version():

    print("DocuMind AI v1.0")


if __name__ == "__main__":
    app()
