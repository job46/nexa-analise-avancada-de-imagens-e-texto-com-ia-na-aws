from pathlib import Path
import boto3
from mypy_boto3_rekognition.type_defs import (
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)
from PIL import Image, ImageDraw, ImageFont

client = boto3.client("rekognition")
FONT_PATH = "Ubuntu-R.ttf"
IMAGE_DIR = Path(__file__).parent / "images"
OUTPUT_SUFFIX = "-resultado.jpg"
CONFIDENCE_THRESHOLD = 90


def get_path(file_name: str) -> Path:
    return IMAGE_DIR / file_name


def recognize_celebrities(photo: Path) -> RecognizeCelebritiesResponseTypeDef:
    try:
        with photo.open("rb") as image:
            return client.recognize_celebrities(Image={"Bytes": image.read()})
    except IOError as e:
        print(f"Erro ao abrir imagem {photo}: {e}")
        return {"CelebrityFaces": []}  # Retorno vazio em caso de erro


def draw_boxes(image_path: Path, output_path: Path, face_details: list[CelebrityTypeDef]) -> None:
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(FONT_PATH, 20)

        width, height = image.size

        for face in face_details:
            box = face["Face"]["BoundingBox"]
            left = int(box["Left"] * width)
            top = int(box["Top"] * height)
            right = int((box["Left"] + box["Width"]) * width)
            bottom = int((box["Top"] + box["Height"]) * height)

            confidence = face.get("MatchConfidence", 0)
            if confidence > CONFIDENCE_THRESHOLD:
                draw.rectangle([left, top, right, bottom], outline="red", width=3)
                text = face.get("Name", "")
                position = (left, max(top - 20, 0))
                bbox = draw.textbbox(position, text, font=font)
                draw.rectangle(bbox, fill="red")
                draw.text(position, text, font=font, fill="white")

        image.save(output_path)
        print(f"Imagem salva com resultados em: {output_path}")
    except (IOError, KeyError) as e:
        print(f"Erro ao processar imagem {image_path}: {e}")


if __name__ == "__main__":
    photo_paths = [
        get_path("bbc.jpg"),
        get_path("msn.jpg"),
        get_path("neymar-torcedores.jpg"),
    ]

    for photo_path in photo_paths:
        if not photo_path.exists():
            print(f"Arquivo não encontrado: {photo_path}")
            continue

        response = recognize_celebrities(photo_path)
        faces = response.get("CelebrityFaces", [])

        if not faces:
            print(f"Nenhum famoso encontrado para a imagem: {photo_path}")
            continue

        output_path = photo_path.with_stem(photo_path.stem + OUTPUT_SUFFIX)
        draw_boxes(photo_path, output_path, faces)
