import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef

FILE_PATH = Path(__file__).parent / "images" / "lista-material-escolar.jpeg"
RESPONSE_FILE = Path("response.json")


def detect_file_text() -> None:
    client = boto3.client("textract")
    try:
        with FILE_PATH.open("rb") as f:
            document_bytes = f.read()

        response = client.detect_document_text(Document={"Bytes": document_bytes})
        RESPONSE_FILE.write_text(json.dumps(response, indent=4, ensure_ascii=False))
        print("Documento processado com sucesso.")
    except (ClientError, IOError) as e:
        print(f"Erro processando documento: {e}")


def get_lines() -> list[str]:
    if not RESPONSE_FILE.exists():
        detect_file_text()

    try:
        with RESPONSE_FILE.open("r") as f:
            data: DetectDocumentTextResponseTypeDef = json.load(f)
            blocks = data.get("Blocks", [])
            return [block["Text"] for block in blocks if block.get("BlockType") == "LINE"]
    except (IOError, KeyError, TypeError) as e:
        print(f"Erro ao ler linhas do arquivo: {e}")
        return []


if __name__ == "__main__":
    lines = get_lines()
    if lines:
        print("\n".join(lines))
    else:
        print("Nenhuma linha encontrada.")
