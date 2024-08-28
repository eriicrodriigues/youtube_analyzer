import pytubefix
from moviepy.editor import *
import openai
from fpdf import FPDF
from dotenv import load_dotenv
import os

# Chave da API da OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(audio_file_path):
    # Faz o upload do arquivo de áudio para a OpenAI e realiza a transcrição
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def save_summary_to_pdf(summary, pdf_file_path):
    # Cria um objeto PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Adiciona um título
    pdf.cell(200, 10, txt="Resumo do Vídeo", ln=True, align='C')
    
    # Adiciona o resumo
    pdf.ln(10)
    pdf.multi_cell(0, 10, summary)
    
    # Salva o arquivo PDF
    pdf.output(pdf_file_path)

# Solicita a URL do vídeo ao usuário
url = input("Digite a URL do vídeo do YouTube: ").strip()

# Verifica se a URL foi fornecida
if not url:
    print("Erro: Nenhuma URL fornecida.")
    sys.exit(1)

# Baixa o áudio do vídeo do YouTube
audio_path = "temp_audio.mp4"
yt = pytubefix.YouTube(url)

try:
    stream = yt.streams.filter(only_audio=True).first().download(filename=audio_path)
except Exception as e:
    print(f"Erro ao baixar o áudio: {e}")
    sys.exit(1)

# Verifica se o arquivo foi baixado com sucesso
if not os.path.exists(audio_path):
    print(f"Erro: O arquivo de áudio não foi encontrado: {audio_path}")
    sys.exit(1)

# Converte o áudio para o formato WAV usando moviepy
wav_output_path = "audio.wav"
try:
    audio_clip = AudioFileClip(audio_path)
    audio_clip.write_audiofile(wav_output_path, codec='pcm_s16le')
except Exception as e:
    print(f"Erro ao converter o áudio: {e}")
    sys.exit(1)

# Remove o arquivo de áudio temporário
os.remove(audio_path)

# Transcreve o áudio usando a API da OpenAI
try:
    transcript = transcribe_audio(wav_output_path)
except Exception as e:
    print(f"Erro ao transcrever o áudio: {e}")
    sys.exit(1)

# Gera o resumo
summary = transcript[:500] 

# Salva o resumo em um arquivo PDF
pdf_file_path = "resumo.pdf"
save_summary_to_pdf(summary, pdf_file_path)

print("Resumo gerado com sucesso!")